"""Public-domain approximate performance of real engines for comparison.

Values are order-of-magnitude figures from open literature / manufacturer
datasheets (rounded). They are **not** certified data. Use only to sanity-check
CEA equilibrium estimates.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceEngine:
    key: str
    name: str
    organization: str
    cycle: str
    fuel: str
    oxidizer: str
    isp_sl_s: float | None
    isp_vac_s: float | None
    thrust_sl_kn: float | None
    thrust_vac_kn: float | None
    pc_bar: float | None
    notes: str


# Approximate open-literature figures (rounded). Update with citations as needed.
REFERENCE_ENGINES: tuple[ReferenceEngine, ...] = (
    ReferenceEngine(
        "rs25", "RS-25 (SSME)", "NASA/Rocketdyne", "Fuel-rich staged combustion",
        "LH2", "LOX", 366.0, 452.0, 1860.0, 2280.0, 206.0,
        "High-Pc hydrolox; vacuum Isp often quoted ~452 s",
    ),
    ReferenceEngine(
        "rl10", "RL10", "Aerojet Rocketdyne", "Expander",
        "LH2", "LOX", None, 450.0, None, 110.0, 44.0,
        "Upper stage; vacuum-optimized",
    ),
    ReferenceEngine(
        "raptor_vac", "Raptor Vacuum (approx)", "SpaceX", "Full-flow staged combustion",
        "LCH4", "LOX", None, 380.0, None, 2500.0, 300.0,
        "Public estimates vary; methalox reference only",
    ),
    ReferenceEngine(
        "merlin_1d_sl", "Merlin 1D SL (approx)", "SpaceX", "Gas generator",
        "RP-1", "LOX", 282.0, 311.0, 845.0, 934.0, 97.0,
        "Booster; sea-level nozzle",
    ),
    ReferenceEngine(
        "rd180", "RD-180 (approx)", "NPO Energomash", "Ox-rich staged combustion",
        "RP-1", "LOX", 311.0, 338.0, 3830.0, 4150.0, 257.0,
        "Atlas V class; high Pc kerolox",
    ),
    ReferenceEngine(
        "aj10", "AJ10 (approx)", "Aerojet", "Pressure-fed",
        "Aerozine-50", "N2O4", None, 320.0, None, 44.0, 9.0,
        "Storable hypergolic upper/OMS-class",
    ),
    ReferenceEngine(
        "f1", "F-1 (Saturn V)", "Rocketdyne", "Gas generator",
        "RP-1", "LOX", 263.0, 304.0, 6770.0, 7770.0, 70.0,
        "Historical sea-level booster",
    ),
    ReferenceEngine(
        "vulcain2", "Vulcain 2 (approx)", "ArianeGroup", "Gas generator",
        "LH2", "LOX", 320.0, 431.0, 960.0, 1350.0, 117.0,
        "Ariane 5 core",
    ),
)


def list_reference_engines() -> list[ReferenceEngine]:
    return list(REFERENCE_ENGINES)


def get_reference_engine(key: str) -> ReferenceEngine:
    for e in REFERENCE_ENGINES:
        if e.key == key:
            return e
    known = ", ".join(e.key for e in REFERENCE_ENGINES)
    raise KeyError(f"Unknown engine '{key}'. Known: {known}")


def compare_isp_to_references(
    isp_s: float,
    mode: str = "vac",
    top_n: int = 5,
) -> list[dict]:
    """Return nearest reference engines by |Isp - ref|."""
    rows = []
    for e in REFERENCE_ENGINES:
        ref = e.isp_vac_s if mode == "vac" else e.isp_sl_s
        if ref is None:
            continue
        rows.append(
            {
                "key": e.key,
                "name": e.name,
                "ref_isp_s": ref,
                "delta_isp_s": isp_s - ref,
                "abs_delta": abs(isp_s - ref),
                "cycle": e.cycle,
                "propellants": f"{e.oxidizer}/{e.fuel}",
                "notes": e.notes,
            }
        )
    rows.sort(key=lambda r: r["abs_delta"])
    return rows[:top_n]
