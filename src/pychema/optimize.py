"""Single- and multi-objective optimization over CEA design variables."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Literal

import numpy as np
from scipy.optimize import differential_evolution, minimize_scalar

from pychema.cea_runner import run_rocket
from pychema.models import EngineInputs, EngineResult


ObjectiveName = Literal["isp", "isp_vac", "cstar", "neg_tc", "density_isp"]


def _objective_value(result: EngineResult, name: ObjectiveName) -> float:
    if not result.success:
        return -1e30
    mapping = {
        "isp": result.isp_s,
        "isp_vac": result.isp_vac_s,
        "cstar": result.cstar_m_s,
        "neg_tc": -result.tc_k if result.tc_k is not None else None,
        "density_isp": result.density_isp_s,
    }
    val = mapping[name]
    if val is None or not np.isfinite(val):
        return -1e30
    return float(val)


@dataclass
class OptimizeResult:
    success: bool
    message: str
    best_inputs: EngineInputs | None
    best_result: EngineResult | None
    objective: str
    best_value: float | None
    history: list[dict]


def optimize_of(
    base: EngineInputs,
    of_min: float,
    of_max: float,
    objective: ObjectiveName = "isp",
    method: str = "bounded",
) -> OptimizeResult:
    """Maximize a scalar objective over O/F at fixed Pc and area ratio."""

    history: list[dict] = []

    def neg_obj(of: float) -> float:
        r = run_rocket(replace(base, of_ratio=float(of)))
        val = _objective_value(r, objective)
        history.append({"of_ratio": float(of), "value": val, "success": r.success})
        return -val

    try:
        res = minimize_scalar(neg_obj, bounds=(of_min, of_max), method="bounded", options={"xatol": 1e-3})
        best_of = float(res.x)
        best = run_rocket(replace(base, of_ratio=best_of))
        return OptimizeResult(
            success=best.success and bool(res.success),
            message="ok" if best.success else best.message,
            best_inputs=best.inputs,
            best_result=best,
            objective=objective,
            best_value=_objective_value(best, objective) if best.success else None,
            history=history,
        )
    except Exception as exc:  # noqa: BLE001
        return OptimizeResult(
            success=False,
            message=str(exc),
            best_inputs=None,
            best_result=None,
            objective=objective,
            best_value=None,
            history=history,
        )


def optimize_of_pc(
    base: EngineInputs,
    of_bounds: tuple[float, float],
    pc_bounds: tuple[float, float],
    objective: ObjectiveName = "isp",
    maxiter: int = 15,
) -> OptimizeResult:
    """Maximize objective over O/F and chamber pressure (differential evolution)."""

    history: list[dict] = []

    def neg_obj(x: np.ndarray) -> float:
        of, pc = float(x[0]), float(x[1])
        r = run_rocket(replace(base, of_ratio=of, pc_bar=pc))
        val = _objective_value(r, objective)
        history.append({"of_ratio": of, "pc_bar": pc, "value": val, "success": r.success})
        return -val

    try:
        res = differential_evolution(
            neg_obj,
            bounds=[of_bounds, pc_bounds],
            maxiter=maxiter,
            polish=True,
            seed=42,
            workers=1,
        )
        of, pc = float(res.x[0]), float(res.x[1])
        best = run_rocket(replace(base, of_ratio=of, pc_bar=pc))
        return OptimizeResult(
            success=best.success,
            message="ok" if best.success else best.message,
            best_inputs=best.inputs,
            best_result=best,
            objective=objective,
            best_value=_objective_value(best, objective) if best.success else None,
            history=history,
        )
    except Exception as exc:  # noqa: BLE001
        return OptimizeResult(
            success=False,
            message=str(exc),
            best_inputs=None,
            best_result=None,
            objective=objective,
            best_value=None,
            history=history,
        )


def pareto_front_2d(
    points: list[tuple[float, float, EngineResult]],
    maximize: tuple[bool, bool] = (True, True),
) -> list[tuple[float, float, EngineResult]]:
    """Simple 2-objective Pareto filter.

    points: list of (obj1, obj2, result)
    maximize: whether each objective is maximized
    """
    if not points:
        return []

    def dominates(a, b) -> bool:
        better_or_eq = True
        strictly_better = False
        for i in range(2):
            ai, bi = a[i], b[i]
            if maximize[i]:
                if ai < bi:
                    better_or_eq = False
                if ai > bi:
                    strictly_better = True
            else:
                if ai > bi:
                    better_or_eq = False
                if ai < bi:
                    strictly_better = True
        return better_or_eq and strictly_better

    front = []
    for i, p in enumerate(points):
        if any(dominates(points[j], p) for j in range(len(points)) if j != i):
            continue
        front.append(p)
    # sort by first objective
    front.sort(key=lambda t: t[0], reverse=maximize[0])
    return front


def multi_objective_of_sweep(
    base: EngineInputs,
    of_min: float,
    of_max: float,
    n: int = 25,
    obj1: ObjectiveName = "isp",
    obj2: ObjectiveName = "neg_tc",
) -> list[tuple[float, float, float, EngineResult]]:
    """Sweep O/F and return (of, o1, o2, result) plus Pareto subset via separate call."""
    ofs = np.linspace(of_min, of_max, n)
    out: list[tuple[float, float, float, EngineResult]] = []
    for of in ofs:
        r = run_rocket(replace(base, of_ratio=float(of)))
        if not r.success:
            continue
        o1 = _objective_value(r, obj1)
        o2 = _objective_value(r, obj2)
        # For reporting, store actual Tc when obj2 is neg_tc
        out.append((float(of), o1, o2, r))
    return out
