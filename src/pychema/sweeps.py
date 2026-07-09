"""Parameter sweeps for O/F, chamber pressure, and area ratio."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from typing import Callable, Iterable, Sequence

import numpy as np
import pandas as pd

from pychema.cea_runner import run_rocket
from pychema.models import EngineInputs, EngineResult, SweepResult


def _linspace(lo: float, hi: float, n: int) -> list[float]:
    return [float(x) for x in np.linspace(lo, hi, n)]


def sweep_of(
    base: EngineInputs,
    of_min: float,
    of_max: float,
    n: int = 21,
    progress: Callable[[int, int], None] | None = None,
) -> SweepResult:
    values = _linspace(of_min, of_max, n)
    results: list[EngineResult] = []
    for i, of in enumerate(values):
        results.append(run_rocket(replace(base, of_ratio=of)))
        if progress:
            progress(i + 1, n)
    return SweepResult(parameter="of_ratio", values=values, results=results)


def sweep_pc(
    base: EngineInputs,
    pc_min: float,
    pc_max: float,
    n: int = 11,
    progress: Callable[[int, int], None] | None = None,
) -> SweepResult:
    values = _linspace(pc_min, pc_max, n)
    results: list[EngineResult] = []
    for i, pc in enumerate(values):
        results.append(run_rocket(replace(base, pc_bar=pc)))
        if progress:
            progress(i + 1, n)
    return SweepResult(parameter="pc_bar", values=values, results=results)


def sweep_area_ratio(
    base: EngineInputs,
    eps_min: float,
    eps_max: float,
    n: int = 11,
    progress: Callable[[int, int], None] | None = None,
) -> SweepResult:
    values = _linspace(eps_min, eps_max, n)
    results: list[EngineResult] = []
    for i, eps in enumerate(values):
        results.append(run_rocket(replace(base, area_ratio=eps)))
        if progress:
            progress(i + 1, n)
    return SweepResult(parameter="area_ratio", values=values, results=results)


def sweep_to_dataframe(sweep: SweepResult) -> pd.DataFrame:
    rows = []
    for v, r in zip(sweep.values, sweep.results):
        rows.append(
            {
                sweep.parameter: v,
                "success": r.success,
                "message": r.message,
                "isp_s": r.isp_s,
                "isp_vac_s": r.isp_vac_s,
                "isp_m_s": r.isp_m_s,
                "isp_vac_m_s": r.isp_vac_m_s,
                "cstar_m_s": r.cstar_m_s,
                "tc_k": r.tc_k,
                "te_k": r.te_k,
                "cf": r.cf,
                "gamma_s": r.gamma_s,
                "mw": r.mw,
                "density_isp_s": r.density_isp_s,
                "area_ratio_actual": r.area_ratio,
                "fuel": r.inputs.fuel,
                "oxidizer": r.inputs.oxidizer,
                "of_ratio": r.inputs.of_ratio,
                "pc_bar": r.inputs.pc_bar,
            }
        )
    return pd.DataFrame(rows)
