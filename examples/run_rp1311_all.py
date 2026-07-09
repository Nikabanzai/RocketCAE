"""Run all official CEA RP-1311 sample drivers (1-14)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pychema.rp1311_smoke import format_smoke_report, run_all_official_samples, smoke_passed


def main() -> int:
    results = run_all_official_samples()
    print(format_smoke_report(results))
    return 0 if smoke_passed(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
