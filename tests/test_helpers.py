"""Tests for sizing / geometry / mission helpers."""

from rocketcae.geometry import nozzle_from_thrust
from rocketcae.references import compare_isp_to_references, list_reference_engines
from rocketcae.sizing import burn_from_thrust, size_stage_from_delta_v, mixture_tank_volumes


def test_size_stage_basic():
    s = size_stage_from_delta_v(3000.0, 320.0, 100.0, 0.10)
    assert s.success
    assert s.propellant_mass_kg > 0
    assert s.gross_mass_kg > s.payload_kg


def test_size_stage_impossible_dv():
    s = size_stage_from_delta_v(20000.0, 200.0, 100.0, 0.15)
    assert not s.success


def test_burn_profile():
    b = burn_from_thrust(1000.0, 300.0, 50_000.0)
    assert b.success
    assert b.burn_time_s > 0
    assert b.mdot_kg_s > 0


def test_nozzle_geometry():
    n = nozzle_from_thrust(50_000.0, 50.0, 1.6, 40.0, lstar_m=1.0)
    assert n.success
    assert n.throat_diameter_m > 0
    assert n.exit_diameter_m > n.throat_diameter_m


def test_tanks():
    t = mixture_tank_volumes(1000.0, 2.3, 810.0, 1141.0)
    assert t["m_fuel_kg"] + t["m_oxidizer_kg"] == 1000.0
    assert t["v_fuel_L"] > 0


def test_references():
    assert len(list_reference_engines()) >= 5
    rows = compare_isp_to_references(450.0, mode="vac", top_n=3)
    assert len(rows) == 3
