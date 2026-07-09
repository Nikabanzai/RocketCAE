"""One-shot engine design: thrust + Pc + propellants -> CEA + geometry + contour.

Inspired by openrocketengine's design API; thermochemistry via official nasa/cea.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pychema.cea_runner import run_from_pair
from pychema.geometry import characteristic_length_suggestion, nozzle_from_thrust
from pychema.models import EngineResult
from pychema.nozzle import NozzleContour, contour_from_throat_area
from pychema.propellants import G0, get_pair
from pychema.references import compare_isp_to_references


@dataclass
class DesignedEngine:
    pair_key: str
    thrust_n: float
    cea: EngineResult
    throat_area_m2: float | None
    throat_diameter_m: float | None
    exit_area_m2: float | None
    exit_diameter_m: float | None
    mdot_kg_s: float | None
    contour: NozzleContour | None
    comparisons: list[dict]
    success: bool
    message: str

    def export_contour_csv(self, path: str | Path) -> Path | None:
        if self.contour is None:
            return None
        return self.contour.to_csv(path)

    def export_contour_cad(self, path: str | Path) -> Path | None:
        if self.contour is None:
            return None
        return self.contour.to_xyz_cad(path)


def design_engine(
    pair_key: str = "lox_rp1",
    thrust_n: float = 50_000.0,
    pc_bar: float = 50.0,
    of_ratio: float | None = None,
    area_ratio: float = 40.0,
    use_vacuum_cf: bool = False,
    bell_fraction: float = 0.8,
    include_chamber: bool = True,
    contraction_ratio: float = 4.0,
) -> DesignedEngine:
    """Design from propellant pair + thrust + chamber pressure.

    1. Run CEA for Isp, Cf, gamma context
    2. At = F / (Pc * Cf)  (SI)
    3. mdot = F / (Isp * g0) using delivered or vacuum Isp consistently with Cf choice
    4. Build Rao contour
    """
    pair = get_pair(pair_key)
    of = float(of_ratio if of_ratio is not None else pair.of_default)
    cea = run_from_pair(pair_key, of_ratio=of, pc_bar=pc_bar, area_ratio=area_ratio)
    if not cea.success or cea.cf is None or cea.isp_s is None:
        return DesignedEngine(
            pair_key, thrust_n, cea, None, None, None, None, None, None, [], False,
            cea.message or "CEA failed",
        )

    cf = cea.cf
    isp = cea.isp_vac_s if use_vacuum_cf and cea.isp_vac_s else cea.isp_s
    # Prefer delivered Cf with delivered Isp for sea-level-ish design
    geom = nozzle_from_thrust(
        thrust_n,
        cea.pc_bar or pc_bar,
        cf,
        cea.area_ratio or area_ratio,
        lstar_m=characteristic_length_suggestion(pair_key),
    )
    if not geom.success or geom.throat_area_m2 is None:
        return DesignedEngine(
            pair_key, thrust_n, cea, None, None, None, None, None, None, [], False, geom.message
        )

    mdot = thrust_n / (isp * G0)
    try:
        contour = contour_from_throat_area(
            geom.throat_area_m2,
            area_ratio,
            kind="rao",
            bell_fraction=bell_fraction,
            include_chamber=include_chamber,
            contraction_ratio=contraction_ratio,
        )
    except Exception as exc:  # noqa: BLE001
        return DesignedEngine(
            pair_key,
            thrust_n,
            cea,
            geom.throat_area_m2,
            geom.throat_diameter_m,
            geom.exit_area_m2,
            geom.exit_diameter_m,
            mdot,
            None,
            compare_isp_to_references(cea.isp_vac_s or isp),
            False,
            f"contour failed: {exc}",
        )

    return DesignedEngine(
        pair_key=pair_key,
        thrust_n=thrust_n,
        cea=cea,
        throat_area_m2=geom.throat_area_m2,
        throat_diameter_m=geom.throat_diameter_m,
        exit_area_m2=geom.exit_area_m2,
        exit_diameter_m=geom.exit_diameter_m,
        mdot_kg_s=mdot,
        contour=contour,
        comparisons=compare_isp_to_references(cea.isp_vac_s or isp),
        success=True,
        message="ok",
    )
