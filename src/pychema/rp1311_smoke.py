"""Execute official CEA RP-1311 sample drivers (smoke + optional numerical)."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from pychema.rp1311_catalog import RP1311_SAMPLES, get_sample, official_sample_path


@dataclass
class SmokeResult:
    number: int
    ok: bool
    seconds: float
    message: str
    path: str


def run_official_sample(number: int, timeout_s: float = 120.0) -> SmokeResult:
    """Run ``cea/samples/rp1311/exampleN.py`` as a subprocess."""
    path = official_sample_path(number)
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        dt = time.perf_counter() - t0
        if proc.returncode == 0:
            return SmokeResult(number, True, dt, "ok", str(path))
        tail = (proc.stderr or proc.stdout or "")[-500:]
        return SmokeResult(number, False, dt, f"exit {proc.returncode}: {tail}", str(path))
    except subprocess.TimeoutExpired:
        dt = time.perf_counter() - t0
        return SmokeResult(number, False, dt, f"timeout >{timeout_s}s", str(path))
    except Exception as exc:  # noqa: BLE001
        dt = time.perf_counter() - t0
        return SmokeResult(number, False, dt, str(exc), str(path))


def run_all_official_samples(
    numbers: list[int] | None = None,
    timeout_s: float = 120.0,
) -> list[SmokeResult]:
    nums = numbers if numbers is not None else [s.number for s in RP1311_SAMPLES]
    return [run_official_sample(n, timeout_s=timeout_s) for n in nums]


def format_smoke_report(results: list[SmokeResult]) -> str:
    lines = [
        "RP-1311 official sample smoke tests (cea package drivers)",
        f"{'#':>3} {'ok':>5} {'sec':>7}  family / title",
        "-" * 72,
    ]
    by_num = {s.number: s for s in RP1311_SAMPLES}
    for r in results:
        meta = by_num.get(r.number)
        title = f"{meta.family}: {meta.title}" if meta else ""
        lines.append(
            f"{r.number:>3} {'PASS' if r.ok else 'FAIL':>5} {r.seconds:7.2f}  {title}"
        )
        if not r.ok:
            lines.append(f"     {r.message[:200]}")
    n_ok = sum(1 for r in results if r.ok)
    lines.append("-" * 72)
    lines.append(f"{n_ok}/{len(results)} samples passed")
    return "\n".join(lines)


def smoke_passed(results: list[SmokeResult] | None = None) -> bool:
    results = results if results is not None else run_all_official_samples()
    return all(r.ok for r in results)
