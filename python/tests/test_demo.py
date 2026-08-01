"""Smoke tests for the single-file demonstration program.

The demo runs on real wall-clock timers, so these tests use its --fast
mode and only assert the scenario verdicts the program itself computes:
failover keeps ownership exclusive, and each bug scenario reproduces its
two-owner execution and shows the correct rule refusing the identical
schedule.  The demo is a companion for reading, not part of the evidence
chain; this test only keeps it from rotting.
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


def test_demo_reproduces_step3_bug_and_correct_rule_refuses() -> None:
    proc = _run("--bug", "step3")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "TWO OWNERS" in proc.stdout
    assert "correct rule refuses the same schedule" in proc.stdout


def test_demo_reproduces_stale_owner_bug_and_correct_rule_refuses() -> None:
    proc = _run("--bug", "stale-owner")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "TWO OWNERS" in proc.stdout
    assert "correct rule refuses the same schedule" in proc.stdout
