"""Tests for nozzle contour and design_engine."""

import numpy as np
import pytest

from pychema.design import design_engine
from pychema.nozzle import conical_contour, rao_bell_contour


def test_conical_eps():
    c = conical_contour(0.05, 16.0)
    assert c.exit_radius_m == pytest.approx(0.05 * 4.0, rel=1e-6)
    assert c.length_m > 0


def test_rao_bell_shape():
    c = rao_bell_contour(0.05, 25.0, bell_fraction=0.8, include_chamber=False)
    assert c.contour_type == "rao_bell"
    assert c.exit_radius_m == pytest.approx(0.05 * 5.0, rel=1e-6)
    # throat near min radius
    assert np.min(c.y) == pytest.approx(0.05, rel=0.05)
    assert c.x[-1] > c.x[0]


def test_rao_with_chamber():
    c = rao_bell_contour(0.04, 16.0, include_chamber=True, contraction_ratio=4.0)
    assert c.contour_type == "rao_bell_with_chamber"
    assert np.max(c.y) >= 0.04 * 2.0 * 0.99  # chamber radius ~ 2 Rt


def test_csv_export(tmp_path):
    c = rao_bell_contour(0.03, 20.0)
    p = c.to_csv(tmp_path / "n.csv")
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    assert "x_m" in text
    p2 = c.to_xyz_cad(tmp_path / "n.xyz")
    assert p2.exists()


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("cea") is None,
    reason="cea not installed",
)
def test_design_engine_smoke():
    d = design_engine("lox_rp1", thrust_n=50_000.0, pc_bar=50.0, area_ratio=25.0)
    assert d.success, d.message
    assert d.throat_diameter_m > 0
    assert d.contour is not None
    assert d.mdot_kg_s > 0
