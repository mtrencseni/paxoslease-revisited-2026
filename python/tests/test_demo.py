"""Smoke test for the single-file demonstration program.

The demo runs on real wall-clock timers, so this test uses its --fast
mode and only asserts the verdict the program itself computes: failover
keeps ownership exclusive.  The demo is a companion for reading, not part
of the evidence chain; this test only keeps it from rotting.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1] / "demo.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DEMO), "--fast", *args],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_demo_failover_keeps_ownership_exclusive() -> None:
    proc = _run()
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "RESULT: failover with exclusive ownership" in proc.stdout
