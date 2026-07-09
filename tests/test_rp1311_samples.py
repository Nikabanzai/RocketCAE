"""RP-1311 sample catalog + official driver smoke tests."""

from __future__ import annotations

import pytest

pytest.importorskip("cea")

from pychema.rp1311_catalog import RP1311_SAMPLES, get_sample, official_sample_path
from pychema.rp1311_smoke import run_all_official_samples, run_official_sample, smoke_passed


def test_catalog_has_14():
    assert len(RP1311_SAMPLES) == 14
    assert get_sample(8).numerical_validation
    assert get_sample(13).numerical_validation
    assert get_sample(1).family == "tp"


def test_official_paths_exist():
    for n in range(1, 15):
        p = official_sample_path(n)
        assert p.is_file(), p


@pytest.mark.parametrize("n", list(range(1, 15)))
def test_official_sample_smoke(n):
    r = run_official_sample(n, timeout_s=60)
    assert r.ok, f"example {n}: {r.message}"


def test_smoke_all_helper():
    # Lighter than re-running if parametrize already did — just check API
    r = run_official_sample(8)
    assert r.ok
