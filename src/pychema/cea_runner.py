"""Thin wrapper around NASA CEA RocketSolver for bipropellant cases."""

from __future__ import annotations

import logging
from typing import Iterable

import numpy as np

from pychema.models import EngineInputs, EngineResult
from pychema.propellants import G0, PAIRS, get_pair, mixture_density

logger = logging.getLogger(__name__)


def _require_cea():
    try:
        import cea  # noqa: F401
        return cea
    except ImportError as exc:
        raise ImportError(
            "NASA cea package is required. Install with: pip install cea\n"
            "Requires Python >= 3.11. See https://nasa.github.io/cea/"
        ) from exc


def _nearest_index(arr: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(arr - target)))


def run_rocket(inputs: EngineInputs) -> EngineResult:
    """Run CEA rocket analysis and extract chamber / exit performance.

    Uses infinite-area combustor (IAC) mode by default, equilibrium composition,
    and evaluates performance at the requested nozzle area ratio (Ae/At).
    """
    cea = _require_cea()

    fuel = inputs.fuel
    oxidizer = inputs.oxidizer
    of_ratio = float(inputs.of_ratio)
    pc = float(inputs.pc_bar)
    eps = float(inputs.area_ratio)

    # Resolve default temperatures from curated library when possible
    t_fuel = inputs.fuel_temp_k
    t_ox = inputs.oxidizer_temp_k
    pair_key = None
    for k, p in PAIRS.items():
        if p.fuel.name == fuel and p.oxidizer.name == oxidizer:
            pair_key = k
            if t_fuel is None:
                t_fuel = p.fuel.temp_k
            if t_ox is None:
                t_ox = p.oxidizer.temp_k
            break
    if t_fuel is None:
        t_fuel = 298.15
    if t_ox is None:
        t_ox = 298.15

    try:
        reac_names = [fuel, oxidizer]
        reac = cea.Mixture(reac_names)
        prod = cea.Mixture(reac_names, products_from_reactants=True)
        solver = cea.RocketSolver(prod, reactants=reac)
        solution = cea.RocketSolution(solver)

        fuel_weights = np.array([1.0, 0.0])
        oxidant_weights = np.array([0.0, 1.0])
        weights = reac.of_ratio_to_weights(oxidant_weights, fuel_weights, of_ratio)
        T_reactant = np.array([t_fuel, t_ox], dtype=float)
        hc = reac.calc_property(cea.ENTHALPY, weights, T_reactant) / cea.R

        pi_p = list(inputs.pressure_ratios)
        subar = [float(inputs.subsonic_area_ratio)]
        # Include the requested epsilon among supersonic area ratios
        supar = sorted({float(eps), 10.0, 25.0, 40.0, 50.0, 75.0, 100.0})

        solver.solve(
            solution,
            weights,
            pc,
            pi_p,
            subar=subar,
            supar=supar,
            hc=hc,
            iac=bool(inputs.iac),
        )

        ae = np.asarray(solution.ae_at, dtype=float)
        isp = np.asarray(solution.Isp, dtype=float)
        isp_vac = np.asarray(solution.Isp_vacuum, dtype=float)
        cstar = np.asarray(solution.c_star, dtype=float)
        T = np.asarray(solution.T, dtype=float)
        P = np.asarray(solution.P, dtype=float)
        Cf = np.asarray(solution.coefficient_of_thrust, dtype=float)
        gamma = np.asarray(solution.gamma_s, dtype=float)
        MW = np.asarray(solution.MW, dtype=float)

        # Index 0 is typically chamber; throat near ae_at == 1
        i_exit = _nearest_index(ae, eps)
        i_throat = _nearest_index(ae, 1.0)

        isp_m = float(isp[i_exit])
        isp_vac_m = float(isp_vac[i_exit])
        cstar_m = float(cstar[i_throat if np.isfinite(cstar[i_throat]) else 0])

        dens_isp = None
        if pair_key is not None:
            rho_mix = mixture_density(get_pair(pair_key), of_ratio)
            dens_isp = (isp_m / G0) * (rho_mix / 1000.0)  # density-Isp proxy (s * g/cm3-ish scale via g/cm3: rho/1000)

        result = EngineResult(
            inputs=inputs,
            success=True,
            message="ok",
            tc_k=float(T[0]),
            pc_bar=float(P[0]),
            cstar_m_s=cstar_m,
            area_ratio=float(ae[i_exit]),
            isp_m_s=isp_m,
            isp_s=isp_m / G0,
            isp_vac_m_s=isp_vac_m,
            isp_vac_s=isp_vac_m / G0,
            cf=float(Cf[i_exit]),
            te_k=float(T[i_exit]),
            pe_bar=float(P[i_exit]),
            gamma_s=float(gamma[i_exit]),
            mw=float(MW[0]),
            density_isp_s=dens_isp,
            raw={
                "ae_at": ae.tolist(),
                "Isp": isp.tolist(),
                "Isp_vacuum": isp_vac.tolist(),
                "c_star": cstar.tolist(),
                "T": T.tolist(),
                "P": P.tolist(),
                "exit_index": i_exit,
            },
        )
        return result
    except Exception as exc:  # noqa: BLE001 — surface CEA failures cleanly
        logger.exception("CEA rocket solve failed")
        return EngineResult(
            inputs=inputs,
            success=False,
            message=str(exc),
        )


def run_from_pair(
    pair_key: str,
    of_ratio: float | None = None,
    pc_bar: float = 50.0,
    area_ratio: float = 40.0,
) -> EngineResult:
    """Convenience: run using a curated propellant pair key."""
    pair = get_pair(pair_key)
    inputs = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=float(of_ratio if of_ratio is not None else pair.of_default),
        pc_bar=float(pc_bar),
        area_ratio=float(area_ratio),
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    return run_rocket(inputs)
