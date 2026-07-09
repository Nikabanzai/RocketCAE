"""Rank curated propellant pairs under a common operating point."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd

from pychema.cea_runner import run_rocket
from pychema.models import EngineInputs
from pychema.propellants import list_propellant_pairs


def rank_propellant_pairs(
    pc_bar: float = 50.0,
    area_ratio: float = 40.0,
    use_pair_default_of: bool = True,
    of_ratio: float | None = None,
) -> pd.DataFrame:
    """Evaluate all curated pairs and rank by vacuum Isp (s)."""
    rows = []
    for pair in list_propellant_pairs():
        of = pair.of_default if use_pair_default_of else float(of_ratio or pair.of_default)
        inputs = EngineInputs(
            fuel=pair.fuel.name,
            oxidizer=pair.oxidizer.name,
            of_ratio=of,
            pc_bar=pc_bar,
            area_ratio=area_ratio,
            fuel_temp_k=pair.fuel.temp_k,
            oxidizer_temp_k=pair.oxidizer.temp_k,
        )
        r = run_rocket(inputs)
        rows.append(
            {
                "pair": pair.key,
                "label": pair.label,
                "of_ratio": of,
                "pc_bar": pc_bar,
                "area_ratio": area_ratio,
                "success": r.success,
                "isp_s": r.isp_s,
                "isp_vac_s": r.isp_vac_s,
                "cstar_m_s": r.cstar_m_s,
                "tc_k": r.tc_k,
                "density_isp_s": r.density_isp_s,
                "cf": r.cf,
                "message": r.message,
                "notes": pair.notes,
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty and df["isp_vac_s"].notna().any():
        df = df.sort_values("isp_vac_s", ascending=False, na_position="last").reset_index(drop=True)
        df["rank_isp_vac"] = range(1, len(df) + 1)
    return df
