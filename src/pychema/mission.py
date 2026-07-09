"""High-level 'mission helper': CEA + sizing + geometry + comparison + report."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pychema.cea_runner import run_from_pair, run_rocket
from pychema.geometry import characteristic_length_suggestion, nozzle_from_thrust
from pychema.models import EngineInputs, EngineResult
from pychema.propellants import get_pair
from pychema.references import compare_isp_to_references
from pychema.report import format_design_brief, write_design_brief
from pychema.sizing import burn_from_thrust, mixture_tank_volumes, size_stage_from_delta_v


@dataclass
class MissionHelperResult:
    cea: EngineResult
    sizing: object | None
    burn: object | None
    nozzle: object | None
    tanks: dict | None
    comparisons: list[dict]
    brief_markdown: str
    brief_path: Path | None = None


def run_mission_helper(
    pair_key: str = "lox_rp1",
    of_ratio: float | None = None,
    pc_bar: float = 50.0,
    area_ratio: float = 40.0,
    delta_v_m_s: float = 3000.0,
    payload_kg: float = 100.0,
    structural_fraction: float = 0.10,
    thrust_n: float = 50_000.0,
    use_vacuum_isp: bool = True,
    ullage_fraction: float = 0.05,
    report_path: str | Path | None = "results/design_brief.md",
) -> MissionHelperResult:
    """End-to-end preliminary study for a curated propellant pair."""
    pair = get_pair(pair_key)
    of = float(of_ratio if of_ratio is not None else pair.of_default)
    cea = run_from_pair(pair_key, of_ratio=of, pc_bar=pc_bar, area_ratio=area_ratio)

    sizing = burn = nozzle = tanks = None
    comparisons: list[dict] = []

    if cea.success:
        isp = cea.isp_vac_s if use_vacuum_isp else cea.isp_s
        assert isp is not None
        sizing = size_stage_from_delta_v(delta_v_m_s, isp, payload_kg, structural_fraction)
        if sizing.success and sizing.propellant_mass_kg is not None:
            burn = burn_from_thrust(sizing.propellant_mass_kg, isp, thrust_n)
            tanks = mixture_tank_volumes(
                sizing.propellant_mass_kg,
                of,
                pair.fuel.density_kg_m3,
                pair.oxidizer.density_kg_m3,
                ullage_fraction=ullage_fraction,
            )
        if cea.cf is not None and cea.pc_bar is not None and cea.area_ratio is not None:
            lstar = characteristic_length_suggestion(pair_key)
            nozzle = nozzle_from_thrust(thrust_n, cea.pc_bar, cea.cf, cea.area_ratio, lstar_m=lstar)
        comparisons = compare_isp_to_references(isp, mode="vac" if use_vacuum_isp else "sl")

    brief = format_design_brief(
        title=f"Preliminary design brief — {pair.label}",
        cea=cea,
        sizing=sizing,
        burn=burn,
        nozzle=nozzle,
        tank_volumes=tanks,
        comparisons=comparisons,
        extra_notes=(
            f"Pair key `{pair_key}`. Isp basis: "
            f"{'vacuum' if use_vacuum_isp else 'delivered (nozzle)'} from CEA IAC equilibrium."
        ),
    )
    path = None
    if report_path is not None:
        path = write_design_brief(report_path, brief)

    return MissionHelperResult(
        cea=cea,
        sizing=sizing,
        burn=burn,
        nozzle=nozzle,
        tanks=tanks,
        comparisons=comparisons,
        brief_markdown=brief,
        brief_path=path,
    )
