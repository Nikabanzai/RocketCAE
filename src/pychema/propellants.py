"""Curated liquid bipropellant pairs for preliminary trade studies.

Species names must match the NASA CEA thermodynamic database.
Temperatures are approximate storage / tank conditions (K).
"""

from __future__ import annotations

from dataclasses import dataclass


G0 = 9.80665  # m/s^2 standard gravity


@dataclass(frozen=True)
class Propellant:
    name: str  # CEA species name
    temp_k: float
    density_kg_m3: float  # approximate liquid density for density-Isp ranking
    role: str  # "fuel" or "oxidizer"
    notes: str = ""


@dataclass(frozen=True)
class PropellantPair:
    key: str
    label: str
    fuel: Propellant
    oxidizer: Propellant
    of_default: float
    of_min: float
    of_max: float
    notes: str = ""


# Densities are approximate handbook values for ranking only (not flight design).
_PROPELLANTS: dict[str, Propellant] = {
    "H2(L)": Propellant("H2(L)", 20.27, 70.8, "fuel", "LH2"),
    "CH4(L)": Propellant("CH4(L)", 111.66, 422.0, "fuel", "LCH4"),
    "RP-1": Propellant("RP-1", 298.15, 810.0, "fuel", "kerosene-type"),
    "C2H5OH(L)": Propellant("C2H5OH(L)", 298.15, 789.0, "fuel", "ethanol"),
    "MMH": Propellant("CH6N2(L)", 298.15, 874.0, "fuel", "monomethylhydrazine"),
    "N2H4(L)": Propellant("N2H4(L)", 298.15, 1004.0, "fuel", "hydrazine"),
    "O2(L)": Propellant("O2(L)", 90.17, 1141.0, "oxidizer", "LOX"),
    "N2O4(L)": Propellant("N2O4(L)", 298.15, 1440.0, "oxidizer", "NTO"),
    "H2O2(L)": Propellant("H2O2(L)", 298.15, 1450.0, "oxidizer", "HTP approx"),
    "N2O": Propellant("N2O", 184.67, 1222.0, "oxidizer", "nitrous oxide"),
}

PAIRS: dict[str, PropellantPair] = {
    "lox_lh2": PropellantPair(
        key="lox_lh2",
        label="LOX / LH2",
        fuel=_PROPELLANTS["H2(L)"],
        oxidizer=_PROPELLANTS["O2(L)"],
        of_default=5.5,
        of_min=3.0,
        of_max=8.0,
        notes="High Isp cryogenic; reference RP-1311 example fuels",
    ),
    "lox_rp1": PropellantPair(
        key="lox_rp1",
        label="LOX / RP-1",
        fuel=_PROPELLANTS["RP-1"],
        oxidizer=_PROPELLANTS["O2(L)"],
        of_default=2.3,
        of_min=1.8,
        of_max=3.2,
        notes="Common booster propellant (CHEMA heritage sample)",
    ),
    "lox_ch4": PropellantPair(
        key="lox_ch4",
        label="LOX / LCH4",
        fuel=_PROPELLANTS["CH4(L)"],
        oxidizer=_PROPELLANTS["O2(L)"],
        of_default=3.4,
        of_min=2.5,
        of_max=4.2,
        notes="Methalox — modern reusable engines",
    ),
    "lox_ethanol": PropellantPair(
        key="lox_ethanol",
        label="LOX / Ethanol",
        fuel=_PROPELLANTS["C2H5OH(L)"],
        oxidizer=_PROPELLANTS["O2(L)"],
        of_default=1.7,
        of_min=1.2,
        of_max=2.5,
        notes="Soft-landing / historical style propellant",
    ),
    "nto_mmh": PropellantPair(
        key="nto_mmh",
        label="NTO / MMH",
        fuel=_PROPELLANTS["MMH"],
        oxidizer=_PROPELLANTS["N2O4(L)"],
        of_default=2.0,
        of_min=1.4,
        of_max=2.6,
        notes="Storable hypergolic (spacecraft)",
    ),
    "nto_hydrazine": PropellantPair(
        key="nto_hydrazine",
        label="NTO / Hydrazine",
        fuel=_PROPELLANTS["N2H4(L)"],
        oxidizer=_PROPELLANTS["N2O4(L)"],
        of_default=1.3,
        of_min=0.9,
        of_max=1.8,
        notes="Storable hypergolic",
    ),
}


def list_propellant_pairs() -> list[PropellantPair]:
    return list(PAIRS.values())


def get_pair(key: str) -> PropellantPair:
    if key not in PAIRS:
        known = ", ".join(sorted(PAIRS))
        raise KeyError(f"Unknown propellant pair '{key}'. Known: {known}")
    return PAIRS[key]


def mixture_density(pair: PropellantPair, of_ratio: float) -> float:
    """Approximate bulk liquid density of O/F mixture by mass fractions."""
    # mass_ox / mass_fuel = of_ratio; total mass = of + 1
    w_ox = of_ratio / (of_ratio + 1.0)
    w_f = 1.0 / (of_ratio + 1.0)
    # harmonic-style volume mix: rho = 1 / (w_f/rho_f + w_ox/rho_ox)
    inv = w_f / pair.fuel.density_kg_m3 + w_ox / pair.oxidizer.density_kg_m3
    return 1.0 / inv

