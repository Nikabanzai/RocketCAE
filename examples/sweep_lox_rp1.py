"""Example: O/F sweep for LOX/RP-1 (CHEMA heritage propellants)."""

from pathlib import Path

from pychema.models import EngineInputs
from pychema.propellants import get_pair
from pychema.sweeps import sweep_of, sweep_to_dataframe


def main() -> None:
    pair = get_pair("lox_rp1")
    base = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=pair.of_default,
        pc_bar=66.5,  # ~965 psia as in old chema.inp
        area_ratio=16.0,
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    sweep = sweep_of(base, pair.of_min, pair.of_max, n=11)
    df = sweep_to_dataframe(sweep)
    out = Path("results") / "example_lox_rp1_of_sweep.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df[["of_ratio", "isp_s", "isp_vac_s", "tc_k", "success"]].to_string(index=False))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
