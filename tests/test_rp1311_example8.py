"""Validate against published NASA RP-1311 Examples 8 and 13."""

from __future__ import annotations

import pytest

pytest.importorskip("cea")

from pychema.validation import (
    compare_all,
    compare_rp1311_example8,
    compare_rp1311_example13,
    format_validation_report,
    validation_passed,
)


def test_rp1311_example8_all_checkpoints():
    rows = compare_rp1311_example8()
    failed = [r for r in rows if not r.pass_]
    if failed:
        pytest.fail("Example 8 failed:\n" + format_validation_report(rows, cases="ex8"))
    assert validation_passed(rows, cases="ex8")
    assert len(rows) >= 10


def test_rp1311_chamber_temperature_close():
    rows = compare_rp1311_example8()
    t_row = next(r for r in rows if r.station == "chamber" and r.quantity == "T_K")
    assert abs(t_row.computed - 3383.845) < 5.0


def test_rp1311_isp_at_eps25():
    rows = compare_rp1311_example8()
    isp = next(r for r in rows if r.station == "Ae/At=25" and r.quantity == "Isp_m_s")
    assert abs(isp.computed - 4124.410) / 4124.410 < 0.005


def test_rp1311_example13_all_checkpoints():
    rows = compare_rp1311_example13()
    failed = [r for r in rows if not r.pass_]
    if failed:
        pytest.fail("Example 13 failed:\n" + format_validation_report(rows, cases="ex13"))
    assert validation_passed(rows, cases="ex13")
    assert len(rows) >= 10


def test_rp1311_example13_condensed_beo():
    """Condensed BeO(L) must appear in chamber; solid BeO(a) downstream."""
    rows = compare_rp1311_example13()
    beo_l = next(
        r
        for r in rows
        if r.station == "chamber" and abs(r.reference - 0.19218) < 1e-6
    )
    assert beo_l.pass_
    assert beo_l.computed > 0.15


def test_rp1311_full_suite():
    rows = compare_all("all")
    if not validation_passed(rows, cases="all"):
        pytest.fail(format_validation_report(rows, cases="all"))
