"""Tests for PyCHEMA core (require nasa cea package)."""

from __future__ import annotations

import pytest

cea = pytest.importorskip("cea")

from pychema.cea_runner import run_from_pair, run_rocket
from pychema.models import EngineInputs
from pychema.optimize import optimize_of, pareto_front_2d
from pychema.propellants import get_pair, list_propellant_pairs
from pychema.ranking import rank_propellant_pairs
from pychema.sweeps import sweep_of, sweep_to_dataframe


def test_list_pairs():
    pairs = list_propellant_pairs()
    assert len(pairs) >= 4
    assert get_pair("lox_lh2").fuel.name == "H2(L)"


def test_run_lox_lh2_smoke():
    """RP-1311-style LOX/LH2 case should succeed with high Isp."""
    r = run_from_pair("lox_lh2", of_ratio=5.55, pc_bar=53.3172, area_ratio=25.0)
    assert r.success, r.message
    assert r.isp_s is not None and r.isp_s > 300
    assert r.isp_vac_s is not None and r.isp_vac_s > r.isp_s
    assert r.tc_k is not None and r.tc_k > 2500
    assert r.cstar_m_s is not None and r.cstar_m_s > 1500


def test_run_lox_rp1_chema_heritage():
    """CHEMA sample style: RP-1 / O2(L)."""
    r = run_from_pair("lox_rp1", of_ratio=2.3, pc_bar=66.5, area_ratio=16.0)
    assert r.success, r.message
    assert r.isp_s is not None and r.isp_s > 200


def test_failed_species_name():
    r = run_rocket(
        EngineInputs(
            fuel="NOT_A_REAL_FUEL",
            oxidizer="O2(L)",
            of_ratio=2.0,
            pc_bar=50.0,
            area_ratio=40.0,
        )
    )
    assert not r.success


def test_sweep_of_short():
    pair = get_pair("lox_ch4")
    base = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=pair.of_default,
        pc_bar=40.0,
        area_ratio=40.0,
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    sweep = sweep_of(base, 3.0, 3.6, n=3)
    df = sweep_to_dataframe(sweep)
    assert len(df) == 3
    assert df["success"].any()


def test_optimize_of():
    pair = get_pair("lox_lh2")
    base = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=5.0,
        pc_bar=50.0,
        area_ratio=40.0,
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    res = optimize_of(base, 4.5, 6.5, objective="isp")
    assert res.success, res.message
    assert res.best_inputs is not None
    assert pair.of_min <= res.best_inputs.of_ratio <= pair.of_max


def test_pareto_filter():
    # synthetic points
    class R:
        pass

    pts = [
        (300.0, 3500.0, R()),
        (310.0, 3600.0, R()),  # better isp worse tc
        (305.0, 3400.0, R()),  # mid
        (290.0, 3300.0, R()),
    ]
    front = pareto_front_2d(pts, maximize=(True, False))
    isps = {p[0] for p in front}
    assert 310.0 in isps
    assert 305.0 in isps


def test_rank_pairs():
    df = rank_propellant_pairs(pc_bar=50.0, area_ratio=40.0)
    assert len(df) == len(list_propellant_pairs())
    ok = df[df["success"] == True]
    assert not ok.empty
    assert ok.iloc[0]["isp_vac_s"] >= ok.iloc[-1]["isp_vac_s"]
