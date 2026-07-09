"""Data models for PyCHEMA inputs and results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EngineInputs:
    """Inputs for a single bipropellant rocket performance evaluation."""

    fuel: str
    oxidizer: str
    of_ratio: float
    pc_bar: float
    area_ratio: float = 40.0
    fuel_temp_k: float | None = None
    oxidizer_temp_k: float | None = None
    iac: bool = True  # infinite-area combustor (standard CEA rocket mode)
    subsonic_area_ratio: float = 1.58
    pressure_ratios: tuple[float, ...] = (10.0, 100.0, 1000.0)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EngineResult:
    """Key performance metrics extracted from a CEA rocket solution."""

    inputs: EngineInputs
    success: bool
    message: str = ""
    # Chamber
    tc_k: float | None = None
    pc_bar: float | None = None
    # Throat / characteristic
    cstar_m_s: float | None = None
    # Exit (at requested area ratio when available)
    area_ratio: float | None = None
    isp_m_s: float | None = None
    isp_s: float | None = None  # Isp / g0
    isp_vac_m_s: float | None = None
    isp_vac_s: float | None = None
    cf: float | None = None
    te_k: float | None = None
    pe_bar: float | None = None
    gamma_s: float | None = None
    mw: float | None = None
    # Mixture densities (reactant side estimate for density-Isp ranking)
    density_isp_s: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["inputs"] = self.inputs.to_dict()
        d.pop("raw", None)
        return d


@dataclass
class SweepResult:
    """Tabular result of a parameter sweep."""

    parameter: str
    values: list[float]
    results: list[EngineResult]

    def to_records(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for v, r in zip(self.values, self.results):
            row = r.to_dict()
            row[self.parameter] = v
            rows.append(row)
        return rows
