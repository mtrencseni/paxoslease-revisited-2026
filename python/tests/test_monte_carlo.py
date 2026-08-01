from __future__ import annotations


from paxoslease.monte_carlo import no_quarantine_counterexample, run_many

def test_randomized_schedules_preserve_invariants() -> None:
    result = run_many(schedules=300, steps=80, seed=12345)
    assert result.total_steps == 24_000
    assert result.delivered > 0
    assert result.dropped > 0
    assert result.duplicated > 0
    assert result.acceptor_crashes > 0

def test_no_quarantine_counterfactual_breaks_exclusivity() -> None:
    assert "lease exclusivity violated" in no_quarantine_counterexample()
