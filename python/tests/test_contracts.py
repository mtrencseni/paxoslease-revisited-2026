from __future__ import annotations

import pytest

from paxoslease.counterexamples import COUNTEREXAMPLES, CounterexampleResult
from paxoslease.fencing import FencedResource, UnfencedResource
from paxoslease.messages import Message
from paxoslease.monte_carlo import acquire_on
from paxoslease.simulator import Simulator
from paxoslease.timing import ClockRateBounds, TimingParameters, safe_timing_parameters
from paxoslease.trace import TraceRecorder


def test_safe_quarantine_boundary_is_allowed() -> None:
    Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4)


def test_insufficient_quarantine_rejected_by_default() -> None:
    with pytest.raises(ValueError, match="unsafe quarantine"):
        Simulator(proposer_duration=4, acceptor_duration=4, quarantine=3)


def test_quarantine_below_acceptor_duration_is_allowed() -> None:
    # The quarantine bound tracks the proposer attempt duration, not the
    # acceptor exclusion duration: Q = D_P < D_A is safe under the
    # prepare-time timer rule (TLC: spec/PaxosLeaseQuarantineEqualsProposer.cfg).
    Simulator(proposer_duration=2, acceptor_duration=4, quarantine=2)


def test_unsafe_counterfactual_constructor_allows_bad_quarantine() -> None:
    Simulator(proposer_duration=4, acceptor_duration=4, quarantine=0, unsafe=True)


def test_release_during_quarantine_is_ignored() -> None:
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4)
    acquire_on(sim, "p1")
    ballot = sim.proposers["p1"].active_ballot
    sim.crash_acceptor("a1")
    sim.restart_acceptor("a1")
    # Inject impossible state to verify the chosen semantics: quarantine ignores release too.
    sim.acceptors["a1"].accepted = sim.acceptors["a2"].accepted
    msg = Message("release", "p1", "a1", ballot=ballot)
    sim.acceptors["a1"].on_release(msg, sim.now)
    assert sim.acceptors["a1"].accepted is not None


def test_proposer_restart_never_reuses_ballots() -> None:
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4)
    sim.start_acquire("p1")
    first = sim.proposers["p1"].ballot
    sim.crash_proposer("p1")
    sim.restart_proposer("p1")
    sim.start_acquire("p1")
    second = sim.proposers["p1"].ballot
    assert second != first


def test_restart_guarantees_uniqueness_not_ordering() -> None:
    # The restart component makes ballots unique across a crash, but it does
    # not order them: the attempt counter restarts from zero under a higher
    # restart component, so a post-restart ballot can be lower than a
    # pre-crash one.  That is safe (acceptors reject the low ballot) but it
    # stalls the proposer, which is why liveness needs the catch-up rule of
    # raising the counter above observed ballots.
    from paxoslease.model import Proposer

    p = Proposer(id="p1", proposer_duration=4, acceptor_ids=("a1", "a2"))
    p.next_ballot()
    before_crash = p.next_ballot()
    p.restart()
    after_restart = p.next_ballot()
    assert after_restart != before_crash
    assert after_restart < before_crash  # unique, not greater


def test_timing_derivation_validates_clock_rate_bounds() -> None:
    bounds = ClockRateBounds(r_min=0.99, r_max=1.01)
    params = safe_timing_parameters(1000, bounds, operation_margin=10)
    params.validate()
    assert params.acceptor_duration >= 1031
    assert params.quarantine_duration >= params.proposer_duration


def test_invalid_timer_containment_is_rejected() -> None:
    with pytest.raises(ValueError, match="timer containment"):
        TimingParameters(5, 4, 5).validate()


def test_fenced_resource_rejects_stale_operation() -> None:
    old = (1, 1, "p1")
    new = (2, 1, "p2")
    unfenced = UnfencedResource()
    assert unfenced.apply(new, "new")
    assert unfenced.apply(old, "old-delayed")

    fenced = FencedResource()
    assert fenced.apply(new, "new")
    assert not fenced.apply(old, "old-delayed")


def test_structured_counterexamples_are_reproducible() -> None:
    results = [fn() for fn in COUNTEREXAMPLES]
    assert {r.scenario for r in results} >= {
        "insufficient-quarantine",
        "owner-only-release",
        "duplicate-quorum-counting",
        "ballot-reuse-after-restart",
        "skipped-paxos-recovery",
        "unfenced-external-effect",
    }
    assert all(isinstance(r, CounterexampleResult) for r in results)
    assert all(r.violated_invariant for r in results)
    assert all(r.minimal_fix for r in results)
    allowed = {
        "simulator-execution",
        "composed-model-execution",
        "illustrative-example",
        "unit-rule",
    }
    assert all(r.category in allowed for r in results)
    # The strongest Python witnesses are real protocol executions.
    executions = {r.scenario for r in results if r.category.endswith("execution")}
    assert {"insufficient-quarantine", "late-promise-reuse", "skipped-paxos-recovery"} <= executions


def _late_promise_schedule(sim: Simulator) -> None:
    """The adversarial schedule behind the late-promise-reuse counterexample."""
    sim.start_acquire("p1")
    sim.start_acquire("p2")
    for pid in ("p1", "p2"):
        for aid in ("a1", "a2"):
            sim.deliver_kind("prepare", dst=aid, src=pid)
    for aid in ("a1", "a2"):
        sim.crash_acceptor(aid)
        sim.restart_acceptor(aid)
    sim.tick(4)
    for pid in ("p1", "p2"):
        for aid in ("a1", "a2"):
            sim.deliver_kind("promise", dst=pid, src=aid)


def test_prepare_time_rule_blocks_late_promise_schedule() -> None:
    # Under the prepare-time timer rule, the stale promise quorums arrive
    # after both pending deadlines expired: no Accept is ever sent and
    # nobody activates.  The identical schedule violates exclusivity when
    # timer_at_quorum=True (see counterexamples.late_promise_reuse).
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4)
    _late_promise_schedule(sim)
    from paxoslease.messages import MessageKind

    assert not any(msg.kind == MessageKind.ACCEPT for msg in sim.queue)
    assert sim.active_owners() == set()


def test_renewal_qualifier_blocks_stale_owner_open_schedule() -> None:
    # P2's renewal qualifier: an own reported lease counts as open only
    # while the proposer is active.  Under the fixed rule, p2's fresh
    # attempt sees the stale record its abandoned attempt installed and is
    # blocked by it like any foreign lease: no promise counts, no Accept
    # is sent, and p1 remains the only owner.  The identical schedule
    # violates exclusivity when self_open_when_inactive=True (see
    # counterexamples.stale_owner_open).
    from paxoslease.counterexamples import _stale_owner_open_schedule
    from paxoslease.messages import MessageKind

    sim = Simulator(
        acceptor_ids=("a1", "a2"),
        proposer_duration=2,
        acceptor_duration=2,
        quarantine=2,
    )
    _stale_owner_open_schedule(sim)
    assert not any(
        msg.kind == MessageKind.ACCEPT and msg.src == "p2" for msg in sim.queue
    )
    assert sim.active_owners() == {"p1"}


def test_acceptor_refusal_blocks_stale_owner_schedule_without_p2_qualifier() -> None:
    # The acceptor-side repair alone: even with the UNQUALIFIED own-lease
    # rule (self_open_when_inactive=True), an acceptor that refuses to
    # overwrite a live lease of a different owner never records the
    # abandoned attempt's stale lease, so the retrying proposer sees the
    # competitor's live lease and is blocked by it.
    from paxoslease.counterexamples import _stale_owner_open_schedule
    from paxoslease.messages import MessageKind

    sim = Simulator(
        acceptor_ids=("a1", "a2"),
        proposer_duration=2,
        acceptor_duration=2,
        quarantine=2,
        self_open_when_inactive=True,
        refuse_live_overwrite=True,
    )
    _stale_owner_open_schedule(sim)
    while sim.queue:
        sim.deliver(0)
    assert sim.active_owners() == {"p1"}
    assert not any(
        msg.kind == MessageKind.ACCEPT and msg.src == "p2" for msg in sim.queue
    )


def test_trace_records_mapped_actions_and_invariant_status() -> None:
    trace = TraceRecorder()
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4, trace=trace)
    sim.start_acquire("p1")
    while sim.queue:
        sim.deliver(0)
    assert "p1" in sim.active_owners()
    assert trace.events
    assert all(event.invariant_ok for event in trace.events)
    assert {event.event for event in trace.events} >= {"StartAcquire", "DeliverPrepare"}
