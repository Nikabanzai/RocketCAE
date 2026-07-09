"""Reproduce NASA RP-1311 Example 8 and print validation vs published output.

Reference: https://nasa.github.io/cea/examples/rocket/example8.html
McBride & Gordon, NASA RP-1311, 1996.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pychema.validation import format_validation_report, run_rp1311_example8, validation_passed


def main() -> int:
    print("Running CEA Example 8 (modern Python API)...\n")
    sol = run_rp1311_example8()
    print(f"num_pts = {sol.num_pts}")
    print(f"Ae/At   = {list(sol.ae_at)}")
    print(f"Isp     = {list(sol.Isp)}")
    print(f"Isp_vac = {list(sol.Isp_vacuum)}")
    print(f"c*      = {list(sol.c_star)[:3]} ...")
    print(f"T[0]    = {sol.T[0]:.3f} K (chamber)")
    print()
    print(format_validation_report())
    return 0 if validation_passed() else 1


if __name__ == "__main__":
    raise SystemExit(main())
