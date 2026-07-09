"""Preliminary nozzle / chamber geometry estimates from CEA performance.

These use ideal 1-D relations. Real injectors, cooling jackets, and contours
require dedicated design tools.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

BAR_TO_PA = 1.0e5


@dataclass(frozen=True)
class NozzleGeometry:
    success: bool
    message: str
    thrust_n: float
    pc_bar: float
    cf: float
    area_ratio: float
    throat_area_m2: float | None = None
    throat_diameter_m: float | None = None
    exit_area_m2: float | None = None
    exit_diameter_m: float | None = None
    chamber_volume_m3: float | None = None  # if L* provided
    lstar_m: float | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message": self.message,
            "thrust_n": self.thrust_n,
            "pc_bar": self.pc_bar,
            "cf": self.cf,
            "area_ratio": self.area_ratio,
            "throat_area_m2": self.throat_area_m2,
            "throat_diameter_m": self.throat_diameter_m,
            "exit_area_m2": self.exit_area_m2,
            "exit_diameter_m": self.exit_diameter_m,
            "chamber_volume_m3": self.chamber_volume_m3,
            "lstar_m": self.lstar_m,
        }


def nozzle_from_thrust(
    thrust_n: float,
    pc_bar: float,
    cf: float,
    area_ratio: float,
    lstar_m: float | None = 1.0,
) -> NozzleGeometry:
    """At = F / (Pc * Cf); Ae = ε * At; optional Vc = L* * At."""
    if thrust_n <= 0 or pc_bar <= 0 or cf <= 0 or area_ratio <= 0:
        return NozzleGeometry(
            False, "Thrust, Pc, Cf, and area ratio must be positive",
            thrust_n, pc_bar, cf, area_ratio,
        )
    pc_pa = pc_bar * BAR_TO_PA
    at = thrust_n / (pc_pa * cf)
    dt = 2.0 * math.sqrt(at / math.pi)
    ae = area_ratio * at
    de = 2.0 * math.sqrt(ae / math.pi)
    vc = None
    if lstar_m is not None and lstar_m > 0:
        vc = lstar_m * at
    return NozzleGeometry(
        success=True,
        message="ok",
        thrust_n=thrust_n,
        pc_bar=pc_bar,
        cf=cf,
        area_ratio=area_ratio,
        throat_area_m2=at,
        throat_diameter_m=dt,
        exit_area_m2=ae,
        exit_diameter_m=de,
        chamber_volume_m3=vc,
        lstar_m=lstar_m,
    )


def characteristic_length_suggestion(propellant_key: str) -> float:
    """Very rough L* hints [m] for preliminary chamber volume only."""
    table = {
        "lox_lh2": 0.8,
        "lox_rp1": 1.2,
        "lox_ch4": 1.0,
        "lox_ethanol": 1.2,
        "nto_mmh": 0.9,
        "nto_hydrazine": 0.9,
    }
    return table.get(propellant_key, 1.0)
