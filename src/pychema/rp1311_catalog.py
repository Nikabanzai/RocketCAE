"""Catalog of NASA RP-1311 sample problems (McBride & Gordon, 1996).

Official Python drivers ship with the ``cea`` package under
``cea/samples/rp1311/exampleN.py``. PyCHEMA:

* **Smoke-tests** all 14 by executing those scripts
* **Numerically validates** Examples 8 and 13 against published tables
  (see ``pychema.validation``)
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Literal

ProblemFamily = Literal[
    "tp",
    "tv",
    "hp",
    "uv",
    "detonation",
    "shock",
    "rocket_iac",
    "rocket_fac",
]


@dataclass(frozen=True)
class RP1311Sample:
    number: int
    family: ProblemFamily
    title: str
    summary: str
    reactants: str
    notes: str = ""
    numerical_validation: bool = False  # detailed checkpoints in pychema.validation


# Descriptions adapted from the classic CEA SAMPLE PROBLEMS listing (RP-1311).
RP1311_SAMPLES: tuple[RP1311Sample, ...] = (
    RP1311Sample(
        1,
        "tp",
        "Assigned T and P (tp)",
        "H2 + Air; eq.ratio 1 & 1.5; P=1,0.1,0.01 atm; T=3000,2000 K; product-only list.",
        "H2 / Air",
    ),
    RP1311Sample(
        2,
        "tv",
        "Assigned T and density (tv)",
        "Same reactants as Ex.1; rho from Ex.1; transport properties.",
        "H2 / Air",
    ),
    RP1311Sample(
        3,
        "hp",
        "Combustion at assigned P (hp)",
        "C7H8(L)+C8H18(L) fuels / Air @700 K; o/f=17; P=100,10,1 bar; large omit list.",
        "C7H8(L)+C8H18(L),n-octa / Air",
    ),
    RP1311Sample(
        4,
        "uv",
        "Assigned U and density (uv)",
        "Same mixture as Ex.3; u/R and rho taken from Ex.3 col.1 (consistency check).",
        "C7H8(L)+C8H18(L),n-octa / Air",
    ),
    RP1311Sample(
        5,
        "hp",
        "Solid propellant combustion (hp)",
        "NH4ClO4 + binder + Al + MgO + H2O; multi-ingredient; P in psia.",
        "NH4ClO4 / CHOS-Binder / Al / MgO / H2O",
    ),
    RP1311Sample(
        6,
        "detonation",
        "Chapman–Jouguet detonation",
        "H2/O2 stoichiometric; T1=298.15,500 K; P1=1,20 bar; transport.",
        "H2 / O2",
    ),
    RP1311Sample(
        7,
        "shock",
        "Shock tube (incident, frozen+eq)",
        "H2/O2/Ar gas; P in mmHg; multiple u1; incd froz eql.",
        "H2 + O2 + Ar",
    ),
    RP1311Sample(
        8,
        "rocket_iac",
        "Rocket IAC — LOX/LH2",
        "o/f=5.55157; Pc=53.3172 bar; subar/supar/pi/p; SI equilibrium.",
        "H2(L) / O2(L)",
        notes="Primary PyCHEMA bipropellant validation case.",
        numerical_validation=True,
    ),
    RP1311Sample(
        9,
        "rocket_fac",
        "Rocket FAC — LOX/LH2",
        "Same as Ex.8 with finite-area combustor ac/at=1.58.",
        "H2(L) / O2(L)",
    ),
    RP1311Sample(
        10,
        "rocket_fac",
        "Rocket FAC via mdot/Ac",
        "Same as Ex.9 using ma=1333.9 instead of ac/at.",
        "H2(L) / O2(L)",
    ),
    RP1311Sample(
        11,
        "rocket_iac",
        "Rocket IAC — Li/F2 with ions",
        "Li(cr)/F2(L); psia=1000; ions; transport; area/pressure ratios.",
        "Li(cr) / F2(L)",
    ),
    RP1311Sample(
        12,
        "rocket_iac",
        "Rocket IAC — MMH/NTO eql+frozen",
        "CH6N2(L)/N2O4(L); o/f=2.5; frozen nfz=2; only-list products.",
        "CH6N2(L) / N2O4(L)",
    ),
    RP1311Sample(
        13,
        "rocket_iac",
        "Rocket IAC — tripropellant with insert",
        "N2H4(L)+Be(a)/H2O2(L); %fuel=67; insert BeO(L); condensed species.",
        "N2H4(L)+Be(a) / H2O2(L)",
        notes="Validates insert= and condensed BeO phases.",
        numerical_validation=True,
    ),
    RP1311Sample(
        14,
        "tp",
        "TP with condensed H2O effects",
        "H2(L)/O2(L) moles; low P; temperatures near condensation.",
        "H2(L) / O2(L)",
    ),
)


def get_sample(number: int) -> RP1311Sample:
    for s in RP1311_SAMPLES:
        if s.number == number:
            return s
    raise KeyError(f"No RP-1311 sample #{number}")


def official_sample_path(number: int) -> Path:
    """Path to ``cea``-shipped ``exampleN.py`` driver."""
    if number < 1 or number > 14:
        raise ValueError("RP-1311 sample number must be 1..14")
    import cea

    base = Path(cea.__file__).resolve().parent / "samples" / "rp1311"
    path = base / f"example{number}.py"
    if not path.is_file():
        raise FileNotFoundError(
            f"Official sample not found at {path}. Reinstall package 'cea'."
        )
    return path


def list_samples() -> list[RP1311Sample]:
    return list(RP1311_SAMPLES)
