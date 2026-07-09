"""Validation cases against published NASA RP-1311 / CEA documentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

import numpy as np

# ---------------------------------------------------------------------------
# Example 8 — H2(L)/O2(L) IAC
# https://nasa.github.io/cea/examples/rocket/example8.html
# ---------------------------------------------------------------------------

RP1311_EX8_INPUT = {
    "reac_names": ["H2(L)", "O2(L)"],
    "T_reactant": np.array([20.27, 90.17]),
    "fuel_weights": np.array([1.0, 0.0]),
    "oxidant_weights": np.array([0.0, 1.0]),
    "of_ratio": 5.55157,
    "pc_bar": 53.3172,
    "pi_p": [10.0, 100.0, 1000.0],
    "subar": [1.58],
    "supar": [25.0, 50.0, 75.0],
    "iac": True,
}

RP1311_EX8_REFERENCE = {
    "chamber_T_K": 3383.845,
    "chamber_P_bar": 53.317,
    "cstar_m_s": 2332.34,
    "stations": {
        1.0: {"Isp_m_s": 1537.917, "Isp_vac_m_s": 2878.925, "Cf": 0.6594, "T_K": 3185.673},
        25.0: {"Isp_m_s": 4124.410, "Isp_vac_m_s": 4348.510, "Cf": 1.7684, "T_K": 1468.163},
        50.0: {"Isp_m_s": 4309.122, "Isp_vac_m_s": 4487.303, "Cf": 1.8476, "T_K": 1219.613},
        75.0: {"Isp_m_s": 4399.121, "Isp_vac_m_s": 4554.913, "Cf": 1.8861, "T_K": 1088.640},
    },
}

# ---------------------------------------------------------------------------
# Example 13 — N2H4(L)+Be(a) / H2O2(L) with BeO(L) insert (condensed species)
# https://nasa.github.io/cea/examples/rocket/example13.html
# Published table uses mixed units (atm, ft/s, lb-s/lb).
# ---------------------------------------------------------------------------

RP1311_EX13_INPUT = {
    "reac_names": ["N2H4(L)", "Be(a)", "H2O2(L)"],
    "fuel_weights": np.array([0.8, 0.2, 0.0]),
    "oxidant_weights": np.array([0.0, 0.0, 1.0]),
    "reac_T": np.array([298.15, 298.15, 298.15]),
    "pct_fuel": 67.0,
    "trace": 1e-10,
    "pc_psi": 3000.0,
    "pi_p": [3.0, 10.0, 30.0, 300.0],
    "insert": ["BeO(L)"],
    "iac": True,
}

# Index order: chamber, throat (Ae/At=1), then expansion stations
RP1311_EX13_REFERENCE = {
    "chamber_T_K": 3002.540,
    "chamber_P_atm": 204.138,
    "cstar_ft_s": 6386.75,
    "stations_by_index": {
        # i: Ae/At, T, Isp (s), Isp_vac (s), Cf, BeO(L) mole frac, BeO(a) mole frac
        1: {
            "ae_at": 1.0,
            "T_K": 2851.000,
            "Isp_s": 121.571,
            "Isp_vac_s": 243.396,
            "Cf": 0.6124,
            "BeO_L": 0.17345,
        },
        2: {
            "ae_at": 1.2363,
            "T_K": 2851.000,
            "Isp_s": 181.306,
            "Isp_vac_s": 263.111,
            "Cf": 0.9133,
            "BeO_L": 0.031752,
        },
        4: {
            "ae_at": 5.3385,
            "T_K": 2068.730,
            "Isp_s": 303.294,
            "Isp_vac_s": 338.619,
            "Cf": 1.5279,
            "BeO_a": 0.19869,
        },
        5: {
            "ae_at": 30.0004,
            "T_K": 1398.106,
            "Isp_s": 364.613,
            "Isp_vac_s": 384.464,
            "Cf": 1.8368,
            "BeO_a": 0.19892,
        },
    },
    "chamber_BeO_L": 0.19218,
    "chamber_H2": 0.51468,
    "chamber_N2": 0.22449,
}


@dataclass
class CheckpointCompare:
    case: str
    station: str
    quantity: str
    reference: float
    computed: float
    rel_error: float
    abs_error: float
    pass_: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "case": self.case,
            "station": self.station,
            "quantity": self.quantity,
            "reference": self.reference,
            "computed": self.computed,
            "rel_error": self.rel_error,
            "abs_error": self.abs_error,
            "pass": self.pass_,
        }


def _require_cea():
    try:
        import cea
        return cea
    except ImportError as exc:
        raise ImportError("pip install cea is required for validation") from exc


def _nearest_index(ae: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(ae - target)))


def _add_check(
    rows: list[CheckpointCompare],
    case: str,
    station: str,
    quantity: str,
    reference: float,
    computed: float,
    rtol: float,
    atol_map: dict[str, float],
) -> None:
    abs_err = abs(computed - reference)
    rel = abs_err / max(abs(reference), 1e-30)
    atol = atol_map.get(quantity, 1.0)
    ok = rel <= rtol or abs_err <= atol
    rows.append(
        CheckpointCompare(case, station, quantity, reference, float(computed), rel, abs_err, ok)
    )


def run_rp1311_example8():
    """Execute Example 8 with the modern CEA Python API (str species names)."""
    cea = _require_cea()
    cfg = RP1311_EX8_INPUT

    reac = cea.Mixture(cfg["reac_names"])
    prod = cea.Mixture(cfg["reac_names"], products_from_reactants=True)
    solver = cea.RocketSolver(prod, reactants=reac)
    solution = cea.RocketSolution(solver)

    weights = reac.of_ratio_to_weights(
        cfg["oxidant_weights"], cfg["fuel_weights"], cfg["of_ratio"]
    )
    hc = reac.calc_property(cea.ENTHALPY, weights, cfg["T_reactant"]) / cea.R
    solver.solve(
        solution,
        weights,
        cfg["pc_bar"],
        cfg["pi_p"],
        subar=cfg["subar"],
        supar=cfg["supar"],
        hc=hc,
        iac=cfg["iac"],
    )
    return solution


def run_rp1311_example13():
    """Execute Example 13: multi-fuel + insert BeO(L) for condensed products."""
    cea = _require_cea()
    cfg = RP1311_EX13_INPUT

    reac = cea.Mixture(cfg["reac_names"])
    prod = cea.Mixture(cfg["reac_names"], products_from_reactants=True)
    solver = cea.RocketSolver(
        prod,
        reactants=reac,
        trace=cfg["trace"],
        insert=cfg["insert"],
    )
    solution = cea.RocketSolution(solver)

    of_ratio = (100.0 - cfg["pct_fuel"]) / cfg["pct_fuel"]
    weights = reac.of_ratio_to_weights(
        cfg["oxidant_weights"], cfg["fuel_weights"], of_ratio
    )
    hc = reac.calc_property(cea.ENTHALPY, weights, cfg["reac_T"]) / cea.R
    pc = cea.units.psi_to_bar(cfg["pc_psi"])
    solver.solve(solution, weights, pc, cfg["pi_p"], iac=cfg["iac"], hc=hc)
    return solution


def compare_rp1311_example8(
    rtol: float = 5e-3,
    atol_map: dict[str, float] | None = None,
) -> list[CheckpointCompare]:
    """Compare live CEA solution to published Example 8 checkpoints."""
    atol_map = atol_map or {
        "T_K": 5.0,
        "Isp_m_s": 5.0,
        "Isp_vac_m_s": 5.0,
        "Cf": 0.005,
        "cstar_m_s": 2.0,
        "P_bar": 0.05,
    }

    sol = run_rp1311_example8()
    ae = np.asarray(sol.ae_at, dtype=float)
    Isp = np.asarray(sol.Isp, dtype=float)
    Isp_vac = np.asarray(sol.Isp_vacuum, dtype=float)
    Cf = np.asarray(sol.coefficient_of_thrust, dtype=float)
    T = np.asarray(sol.T, dtype=float)
    P = np.asarray(sol.P, dtype=float)
    cstar = np.asarray(sol.c_star, dtype=float)

    ref = RP1311_EX8_REFERENCE
    rows: list[CheckpointCompare] = []
    case = "ex8"

    _add_check(rows, case, "chamber", "T_K", ref["chamber_T_K"], float(T[0]), rtol, atol_map)
    _add_check(rows, case, "chamber", "P_bar", ref["chamber_P_bar"], float(P[0]), rtol, atol_map)
    _add_check(
        rows,
        case,
        "throat",
        "cstar_m_s",
        ref["cstar_m_s"],
        float(cstar[_nearest_index(ae, 1.0)]),
        rtol,
        atol_map,
    )

    for eps, vals in ref["stations"].items():
        i = _nearest_index(ae, eps)
        st = f"Ae/At={eps:g}"
        _add_check(rows, case, st, "Isp_m_s", vals["Isp_m_s"], float(Isp[i]), rtol, atol_map)
        _add_check(rows, case, st, "Isp_vac_m_s", vals["Isp_vac_m_s"], float(Isp_vac[i]), rtol, atol_map)
        _add_check(rows, case, st, "Cf", vals["Cf"], float(Cf[i]), rtol, atol_map)
        _add_check(rows, case, st, "T_K", vals["T_K"], float(T[i]), rtol, atol_map)

    return rows


def compare_rp1311_example13(
    rtol: float = 5e-3,
    atol_map: dict[str, float] | None = None,
) -> list[CheckpointCompare]:
    """Compare live CEA solution to published Example 13 checkpoints.

    Uses published mixed units where the docs print them (atm, ft/s, s, mole frac).
    """
    cea = _require_cea()
    atol_map = atol_map or {
        "T_K": 5.0,
        "Isp_s": 0.5,
        "Isp_vac_s": 0.5,
        "Cf": 0.005,
        "cstar_ft_s": 5.0,
        "P_atm": 0.05,
        "ae_at": 0.01,
        "mole_frac": 0.002,
    }

    sol = run_rp1311_example13()
    G0 = 9.80665
    ae = np.asarray(sol.ae_at, dtype=float)
    T = np.asarray(sol.T, dtype=float)
    P_atm = np.asarray(cea.units.bar_to_atm(sol.P), dtype=float)
    cstar_ft = np.asarray(cea.units.m_per_s_to_ft_per_s(sol.c_star), dtype=float)
    Cf = np.asarray(sol.coefficient_of_thrust, dtype=float)
    Isp_s = np.asarray(sol.Isp, dtype=float) / G0
    Isp_vac_s = np.asarray(sol.Isp_vacuum, dtype=float) / G0
    mf = sol.mole_fractions

    ref = RP1311_EX13_REFERENCE
    rows: list[CheckpointCompare] = []
    case = "ex13"

    _add_check(rows, case, "chamber", "T_K", ref["chamber_T_K"], float(T[0]), rtol, atol_map)
    _add_check(rows, case, "chamber", "P_atm", ref["chamber_P_atm"], float(P_atm[0]), rtol, atol_map)
    _add_check(
        rows,
        case,
        "throat",
        "cstar_ft_s",
        ref["cstar_ft_s"],
        float(cstar_ft[1]),
        rtol,
        atol_map,
    )
    _add_check(
        rows,
        case,
        "chamber",
        "mole_frac",
        ref["chamber_BeO_L"],
        float(mf["BeO(L)"][0]),
        rtol,
        atol_map,
    )
    _add_check(
        rows,
        case,
        "chamber",
        "mole_frac",
        ref["chamber_H2"],
        float(mf["H2"][0]),
        rtol,
        {**atol_map, "mole_frac": 0.005},
    )
    _add_check(
        rows,
        case,
        "chamber",
        "mole_frac",
        ref["chamber_N2"],
        float(mf["N2"][0]),
        rtol,
        {**atol_map, "mole_frac": 0.005},
    )

    for idx, vals in ref["stations_by_index"].items():
        st = f"i={idx} Ae/At~{vals['ae_at']:g}"
        _add_check(rows, case, st, "ae_at", vals["ae_at"], float(ae[idx]), rtol, atol_map)
        _add_check(rows, case, st, "T_K", vals["T_K"], float(T[idx]), rtol, atol_map)
        _add_check(rows, case, st, "Isp_s", vals["Isp_s"], float(Isp_s[idx]), rtol, atol_map)
        _add_check(rows, case, st, "Isp_vac_s", vals["Isp_vac_s"], float(Isp_vac_s[idx]), rtol, atol_map)
        _add_check(rows, case, st, "Cf", vals["Cf"], float(Cf[idx]), rtol, atol_map)
        if "BeO_L" in vals:
            _add_check(
                rows,
                case,
                st,
                "mole_frac",
                vals["BeO_L"],
                float(mf["BeO(L)"][idx]),
                rtol,
                atol_map,
            )
        if "BeO_a" in vals:
            _add_check(
                rows,
                case,
                st,
                "mole_frac",
                vals["BeO_a"],
                float(mf["BeO(a)"][idx]),
                rtol,
                atol_map,
            )

    return rows


CaseName = Literal["ex8", "ex13", "all"]


def compare_all(cases: CaseName = "all") -> list[CheckpointCompare]:
    rows: list[CheckpointCompare] = []
    if cases in ("ex8", "all"):
        rows.extend(compare_rp1311_example8())
    if cases in ("ex13", "all"):
        rows.extend(compare_rp1311_example13())
    return rows


def validation_passed(
    rows: list[CheckpointCompare] | None = None,
    cases: CaseName = "all",
) -> bool:
    rows = rows if rows is not None else compare_all(cases)
    return all(r.pass_ for r in rows)


def format_validation_report(
    rows: list[CheckpointCompare] | None = None,
    cases: CaseName = "all",
    title: str | None = None,
) -> str:
    rows = rows if rows is not None else compare_all(cases)
    if title is None:
        if cases == "ex8":
            title = "RP-1311 Example 8 validation (H2(L)/O2(L), IAC)"
        elif cases == "ex13":
            title = "RP-1311 Example 13 validation (N2H4+Be/H2O2, BeO insert)"
        else:
            title = "RP-1311 validation suite (Examples 8 + 13)"

    lines = [
        title,
        f"{'case':<6} {'station':<22} {'qty':<12} {'ref':>12} {'cea':>12} {'rel%':>10} {'ok':>4}",
        "-" * 84,
    ]
    for r in rows:
        lines.append(
            f"{r.case:<6} {r.station:<22} {r.quantity:<12} {r.reference:12.4f} {r.computed:12.4f} "
            f"{100 * r.rel_error:9.3f}% {'PASS' if r.pass_ else 'FAIL':>4}"
        )
    n_ok = sum(1 for r in rows if r.pass_)
    lines.append("-" * 84)
    lines.append(f"{n_ok}/{len(rows)} checkpoints passed")
    return "\n".join(lines)


# Re-export smoke suite for a single validation entry point
from pychema.rp1311_smoke import (  # noqa: E402
    format_smoke_report,
    run_all_official_samples,
    run_official_sample,
    smoke_passed,
)
from pychema.rp1311_catalog import RP1311_SAMPLES, list_samples  # noqa: E402


def full_validation_report() -> str:
    """Numerical Ex.8+13 plus smoke of all 14 official drivers."""
    num = format_validation_report(cases="all")
    smoke = run_all_official_samples()
    return num + "\n\n" + format_smoke_report(smoke)


def full_validation_passed() -> bool:
    return validation_passed(cases="all") and smoke_passed()
