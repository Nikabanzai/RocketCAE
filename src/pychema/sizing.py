"""Preliminary mission / propellant sizing helpers (not flight design).

Uses the ideal rocket equation and constant-Isp assumptions. Real vehicles
need gravity, drag, residuals, mixture ratio shifts, and structural mass models.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from pychema.propellants import G0


@dataclass(frozen=True)
class StageSizing:
    """Single-stage ideal sizing from Δv and structural fraction."""

    delta_v_m_s: float
    isp_s: float
    payload_kg: float
    structural_fraction: float  # inert / (inert + propellant), typical 0.05–0.15
    success: bool
    message: str
    mass_ratio: float | None = None  # m0/mf
    propellant_mass_kg: float | None = None
    inert_mass_kg: float | None = None
    gross_mass_kg: float | None = None
    propellant_mass_fraction: float | None = None

    def to_dict(self) -> dict:
        return {
            "delta_v_m_s": self.delta_v_m_s,
            "isp_s": self.isp_s,
            "payload_kg": self.payload_kg,
            "structural_fraction": self.structural_fraction,
            "success": self.success,
            "message": self.message,
            "mass_ratio": self.mass_ratio,
            "propellant_mass_kg": self.propellant_mass_kg,
            "inert_mass_kg": self.inert_mass_kg,
            "gross_mass_kg": self.gross_mass_kg,
            "propellant_mass_fraction": self.propellant_mass_fraction,
        }


@dataclass(frozen=True)
class BurnProfile:
    """Constant-thrust burn from propellant mass and Isp."""

    propellant_mass_kg: float
    isp_s: float
    thrust_n: float
    success: bool
    message: str
    mdot_kg_s: float | None = None
    burn_time_s: float | None = None
    total_impulse_n_s: float | None = None
    ve_m_s: float | None = None

    def to_dict(self) -> dict:
        return {
            "propellant_mass_kg": self.propellant_mass_kg,
            "isp_s": self.isp_s,
            "thrust_n": self.thrust_n,
            "success": self.success,
            "message": self.message,
            "mdot_kg_s": self.mdot_kg_s,
            "burn_time_s": self.burn_time_s,
            "total_impulse_n_s": self.total_impulse_n_s,
            "ve_m_s": self.ve_m_s,
        }


def ideal_mass_ratio(delta_v_m_s: float, isp_s: float) -> float:
    """m0/mf = exp(Δv / (Isp * g0))."""
    if isp_s <= 0:
        raise ValueError("Isp must be positive")
    return math.exp(delta_v_m_s / (isp_s * G0))


def size_stage_from_delta_v(
    delta_v_m_s: float,
    isp_s: float,
    payload_kg: float,
    structural_fraction: float = 0.10,
) -> StageSizing:
    """Ideal single-stage propellant sizing for a target Δv.

    Definitions (common preliminary model):
    - payload = useful load (not including stage inert)
    - structural_fraction λ = m_inert / (m_inert + m_propellant)
    - mf = payload + inert
    - m0 = payload + inert + propellant
    """
    if delta_v_m_s < 0:
        return StageSizing(delta_v_m_s, isp_s, payload_kg, structural_fraction, False, "Δv must be ≥ 0")
    if isp_s <= 0 or payload_kg < 0:
        return StageSizing(delta_v_m_s, isp_s, payload_kg, structural_fraction, False, "Invalid Isp or payload")
    if not (0.0 < structural_fraction < 1.0):
        return StageSizing(
            delta_v_m_s, isp_s, payload_kg, structural_fraction, False,
            "structural_fraction must be in (0, 1)",
        )

    try:
        r = ideal_mass_ratio(delta_v_m_s, isp_s)  # m0/mf
    except ValueError as exc:
        return StageSizing(delta_v_m_s, isp_s, payload_kg, structural_fraction, False, str(exc))

    # m0/mf = r; m_prop = m0 - mf; m_inert = λ/(1-λ) * m_prop
    # mf = payload + inert; m0 = mf * r
    # m_prop = mf*(r-1); inert = λ * (inert+prop) => inert = λ/(1-λ)*prop
    # payload + λ/(1-λ)*prop = prop/(r-1)
    # => payload = prop * (1/(r-1) - λ/(1-λ))
    denom = 1.0 / (r - 1.0) - structural_fraction / (1.0 - structural_fraction)
    if denom <= 0:
        return StageSizing(
            delta_v_m_s,
            isp_s,
            payload_kg,
            structural_fraction,
            False,
            "Δv too large for this Isp and structural fraction (need staging or higher Isp)",
        )

    m_prop = payload_kg / denom
    m_inert = structural_fraction / (1.0 - structural_fraction) * m_prop
    m_gross = payload_kg + m_inert + m_prop
    pmf = m_prop / m_gross

    return StageSizing(
        delta_v_m_s=delta_v_m_s,
        isp_s=isp_s,
        payload_kg=payload_kg,
        structural_fraction=structural_fraction,
        success=True,
        message="ok",
        mass_ratio=r,
        propellant_mass_kg=m_prop,
        inert_mass_kg=m_inert,
        gross_mass_kg=m_gross,
        propellant_mass_fraction=pmf,
    )


def burn_from_thrust(
    propellant_mass_kg: float,
    isp_s: float,
    thrust_n: float,
) -> BurnProfile:
    """Constant thrust and Isp → mdot and burn time."""
    if propellant_mass_kg <= 0 or isp_s <= 0 or thrust_n <= 0:
        return BurnProfile(
            propellant_mass_kg, isp_s, thrust_n, False, "Mass, Isp, and thrust must be positive"
        )
    ve = isp_s * G0
    mdot = thrust_n / ve
    tb = propellant_mass_kg / mdot
    return BurnProfile(
        propellant_mass_kg=propellant_mass_kg,
        isp_s=isp_s,
        thrust_n=thrust_n,
        success=True,
        message="ok",
        mdot_kg_s=mdot,
        burn_time_s=tb,
        total_impulse_n_s=thrust_n * tb,
        ve_m_s=ve,
    )


def thrust_from_mdot(mdot_kg_s: float, isp_s: float) -> float:
    return mdot_kg_s * isp_s * G0


def mixture_tank_volumes(
    propellant_mass_kg: float,
    of_ratio: float,
    fuel_density_kg_m3: float,
    ox_density_kg_m3: float,
    ullage_fraction: float = 0.05,
) -> dict[str, float]:
    """Split biprop mass by O/F and estimate tank volumes (ullage added)."""
    if of_ratio <= 0 or propellant_mass_kg <= 0:
        raise ValueError("of_ratio and propellant mass must be positive")
    m_ox = propellant_mass_kg * of_ratio / (1.0 + of_ratio)
    m_fuel = propellant_mass_kg / (1.0 + of_ratio)
    v_ox = m_ox / ox_density_kg_m3
    v_fuel = m_fuel / fuel_density_kg_m3
    factor = 1.0 + ullage_fraction
    return {
        "m_oxidizer_kg": m_ox,
        "m_fuel_kg": m_fuel,
        "v_oxidizer_m3": v_ox * factor,
        "v_fuel_m3": v_fuel * factor,
        "v_oxidizer_L": v_ox * factor * 1000.0,
        "v_fuel_L": v_fuel * factor * 1000.0,
        "ullage_fraction": ullage_fraction,
    }
