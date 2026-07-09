"""Reproduce NASA RP-1311 Example 13 (insert BeO(L), condensed products).

Reference: https://nasa.github.io/cea/examples/rocket/example13.html
McBride & Gordon, NASA RP-1311, 1996.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pychema.validation import (
    format_validation_report,
    run_rp1311_example13,
    validation_passed,
)


def main() -> int:
    print("Running CEA Example 13 (N2H4+Be / H2O2, BeO insert)...\n")
    sol = run_rp1311_example13()
    print(f"num_pts = {sol.num_pts}")
    print(f"Ae/At   = {[round(float(x), 4) for x in sol.ae_at]}")
    print(f"T [K]   = {[round(float(x), 3) for x in sol.T]}")
    print(f"Isp [s] = {[round(float(x) / 9.80665, 3) for x in sol.Isp]}")
    print(f"BeO(L)  = {[float(x) for x in sol.mole_fractions['BeO(L)']]}")
    print(f"BeO(a)  = {[float(x) for x in sol.mole_fractions['BeO(a)']]}")
    print()
    print(format_validation_report(cases="ex13"))
    return 0 if validation_passed(cases="ex13") else 1


if __name__ == "__main__":
    raise SystemExit(main())
