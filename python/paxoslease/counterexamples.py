from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .event_loop import run_suspended_loop, run_timely_loop
from .fencing import FencedResource, UnfencedResource
from .messages import Message
from .monte_carlo import acquire_on
from .simulator import Simulator


@dataclass(frozen=True)
class CounterexampleResult:
    scenario: str
    violated_invariant: str
    minimal_fix: str
    trace: tuple[str, ...]
    category: str


# The witnesses are NOT all comparable evidence, and the category says which
# kind each one is:
#   simulator-execution  -- a deterministic protocol execution in the
#                           reference simulator violates a checked invariant;
#   composed-model-execution -- same, in the composed lease+Paxos model;
#   illustrative-example -- executable, but the broken rule is applied by the
#                           witness itself rather than by the protocol model;
#   unit-rule            -- a direct assertion connecting a local rule to its
#                           failure, with no protocol execution at all.
# The TLC counterexamples in counterexamples/*.tla are a separate, stronger
# class: there the model checker finds the violating schedule itself.
CATEGORIES = {
    "insufficient-quarantine": "simulator-execution",
    "owner-only-release": "illustrative-example",
    "duplicate-quorum-counting": "unit-rule",
    "ballot-reuse-after-restart": "unit-rule",
    "skipped-paxos-recovery": "composed-model-execution",
    "unfenced-external-effect": "illustrative-example",
    "nonintersecting-reconfiguration": "illustrative-example",
    "unsafe-clock-source": "unit-rule",
    "renewal-without-quorum": "unit-rule",
    "stale-accept-overwrites-newer": "unit-rule",
    "late-promise-reuse": "simulator-execution",
    "stale-owner-open": "simulator-execution",
    "split-brain-read-without-fence": "unit-rule",
    "suspended-event-loop": "simulator-execution",
    "unsigned-expiry-underflow": "unit-rule",
}

# The assertion message each witness is required to fail with.  Matching the
# message keeps an unrelated AssertionError from masquerading as the expected
# violation.
EXPECTED_VIOLATION = {
    "insufficient-quarantine": "lease exclusivity violated",
    "owner-only-release": "owner-only release erased newer lease",
    "duplicate-quorum-counting": "duplicate responses counted as a quorum",
    "ballot-reuse-after-restart": "ballot reused after restart",
    "skipped-paxos-recovery": "skipped recovery ignored a prior accepted value",
    "nonintersecting-reconfiguration": "do not intersect",
    "unsafe-clock-source": "wall-clock step made an expired lease look live",
    "renewal-without-quorum": "failed renewal extended authority",
    "stale-accept-overwrites-newer": "stale lower-ballot accept overwrote newer promise",
    "late-promise-reuse": "lease exclusivity violated",
    "stale-owner-open": "lease exclusivity violated",
    "split-brain-read-without-fence": "unfenced read was concurrent",
    "suspended-event-loop": "lease exclusivity violated during event-loop suspension",
    "unsigned-expiry-underflow": "unsigned expiry subtraction underflowed",
}


def _expect_violation(scenario: str, fn: Callable[[], tuple[str, ...]]) -> CounterexampleResult:
    try:
        trace = fn()
    except AssertionError as exc:
        expected = EXPECTED_VIOLATION[scenario]
        if expected not in str(exc):
            raise AssertionError(
                f"{scenario} failed with an unexpected assertion: {exc!r} "
                f"(expected message containing {expected!r})"
            ) from exc
        return CounterexampleResult(
            scenario=scenario,
            violated_invariant=str(exc),
            minimal_fix=FIXES[scenario],
            trace=(f"violation: {exc}",),
            category=CATEGORIES[scenario],
        )
    raise AssertionError(f"{scenario} did not fail; trace={trace}")


FIXES = {
    "insufficient-quarantine": "quarantine for at least the proposer attempt duration in real time",
    "owner-only-release": "release must name the exact owner and ballot",
    "duplicate-quorum-counting": "count quorum responses by distinct acceptor identity",
    "ballot-reuse-after-restart": "include a durable restart epoch or external uniqueness component in ballots",
    "skipped-paxos-recovery": "client admission requires completed Paxos Phase 1 recovery",
    "unfenced-external-effect": "protected resources must reject stale fencing tokens",
    "nonintersecting-reconfiguration": "configuration changes must preserve quorum intersection or wait out old leases",
    "unsafe-clock-source": "lease timers must be monotonic elapsed-time measurements with bounded rate error",
    "renewal-without-quorum": "renewal may extend authority only after a fresh accept quorum",
    "stale-accept-overwrites-newer": "acceptors must reject lower ballots after promising a higher ballot",
    "late-promise-reuse": "start the attempt deadline when Prepare is sent, so prepare responses expire with the attempt that collected them",
    "stale-owner-open": "count a reported own lease as open only while renewing (currently active); a stale own record must block like a foreign lease",
    "split-brain-read-without-fence": "external reads and writes require either log ordering or fencing",
    "suspended-event-loop": "store the attempt deadline as protocol state and check it in the Phase 2 response handler, instead of relying on timer dispatch order",
    "unsigned-expiry-underflow": "read the clock once per handler, compare before subtracting, and keep deadline arithmetic away from unsigned wraparound",
}


def insufficient_quarantine() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=0, unsafe=True)
        acquire_on(sim, "p1")
        for aid in ("a1", "a2"):
            sim.crash_acceptor(aid)
            sim.restart_acceptor(aid)
        sim.start_acquire("p2")
        for aid in ("a1", "a2"):
            sim.deliver_kind("prepare", dst=aid, src="p2")
        for aid in ("a1", "a2"):
            sim.deliver_kind("promise", dst="p2", src=aid)
        for aid in ("a1", "a2"):
            sim.deliver_kind("accept", dst=aid, src="p2")
        for aid in ("a1", "a2"):
            sim.deliver_kind("accepted", dst="p2", src=aid)
        return ()

    return _expect_violation("insufficient-quarantine", run)


def owner_only_release() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        sim = Simulator(proposer_duration=6, acceptor_duration=6, quarantine=6)
        acquire_on(sim, "p1")
        old = sim.proposers["p1"].active_ballot
        sim.start_acquire("p1")
        for aid in ("a1", "a2"):
            sim.deliver_kind("prepare", dst=aid, src="p1")
        for aid in ("a1", "a2"):
            sim.deliver_kind("promise", dst="p1", src=aid)
        for aid in ("a1", "a2"):
            sim.deliver_kind("accept", dst=aid, src="p1")
        for aid in ("a1", "a2"):
            sim.deliver_kind("accepted", dst="p1", src=aid)
        new = sim.proposers["p1"].active_ballot
        assert old != new
        stale = Message("release", "p1", "a1", ballot=old)
        # Broken behavior: owner-only release clears the newer lease.
        if sim.acceptors["a1"].accepted is not None and sim.acceptors["a1"].accepted.owner == stale.src:
            sim.acceptors["a1"].accepted = None
        assert sim.acceptors["a1"].accepted is not None, "owner-only release erased newer lease"
        return ()

    return _expect_violation("owner-only-release", run)


def duplicate_quorum_counting() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        responders = ["a1", "a1"]
        assert len(responders) == len(set(responders)), "duplicate responses counted as a quorum"
        return ()

    return _expect_violation("duplicate-quorum-counting", run)


def ballot_reuse_after_restart() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        first = (1, 1, "p1")
        after_restart = (1, 1, "p1")  # broken: same counter, same restart component
        assert after_restart != first, "ballot reused after restart"
        return ()

    return _expect_violation("ballot-reuse-after-restart", run)


def skipped_paxos_recovery() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        from .leased_paxos import LeasedPaxosCluster

        cluster = LeasedPaxosCluster()
        assert cluster.acquire_lease("p1")
        cluster.recover_and_become_ready("p1")
        cluster.accept_without_leader_learning("p1", 1, "old", ("pa1",))
        cluster.tick(4)
        assert cluster.acquire_lease("p2")
        cluster.state["p2"] = "ready"  # Broken: skips recovery.
        cluster.leader_ballot["p2"] = (99, 0, "p2")
        slot, value = cluster.append("p2", "new")
        assert not (slot == 1 and value == "new"), "skipped recovery ignored a prior accepted value"
        return ()

    return _expect_violation("skipped-paxos-recovery", run)


def unfenced_external_effect() -> CounterexampleResult:
    old = (1, 1, "p1")
    new = (2, 1, "p2")
    unfenced = UnfencedResource()
    assert unfenced.apply(new, "new-owner-write")
    assert unfenced.apply(old, "delayed-old-owner-write")

    fenced = FencedResource()
    assert fenced.apply(new, "new-owner-write")
    assert not fenced.apply(old, "delayed-old-owner-write")
    return CounterexampleResult(
        scenario="unfenced-external-effect",
        violated_invariant="unfenced resource accepted delayed stale owner operation",
        minimal_fix=FIXES["unfenced-external-effect"],
        trace=("new owner writes", "old delayed write is accepted without fencing", "fenced model rejects it"),
        category=CATEGORIES["unfenced-external-effect"],
    )


def nonintersecting_reconfiguration() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        old_quorum = {"a1", "a2"}
        new_quorum = {"a3", "a4"}
        assert old_quorum & new_quorum, "old and new lease quorums do not intersect"
        return ()

    return _expect_violation("nonintersecting-reconfiguration", run)


def unsafe_clock_source() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        monotonic_elapsed = 4
        wall_clock_elapsed_after_step_back = 1
        assert wall_clock_elapsed_after_step_back >= monotonic_elapsed, (
            "wall-clock step made an expired lease look live"
        )
        return ()

    return _expect_violation("unsafe-clock-source", run)


def renewal_without_quorum() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        old_deadline = 4
        renewal_acks = {"a1"}
        quorum_size_needed = 2
        new_deadline = 8 if renewal_acks else old_deadline
        assert not (len(renewal_acks) < quorum_size_needed and new_deadline > old_deadline), (
            "failed renewal extended authority without a quorum"
        )
        return ()

    return _expect_violation("renewal-without-quorum", run)


def stale_accept_overwrites_newer() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        promised = (7, 1, "p2")
        stale_accept_ballot = (3, 1, "p1")
        accepted = stale_accept_ballot  # Broken acceptor ignores its promise.
        assert not (stale_accept_ballot < promised and accepted == stale_accept_ballot), (
            "stale lower-ballot accept overwrote newer promise"
        )
        return ()

    return _expect_violation("stale-accept-overwrites-newer", run)


def late_promise_reuse() -> CounterexampleResult:
    """Two leaders under the original 2012 step-3 timer rule, despite full quarantine.

    The proposer timer starts only when a prepare quorum is received, so nothing
    bounds how stale that quorum is.  Both proposers legitimately collect empty
    promises, the acceptors crash, forget their promises, restart, and serve the
    entire quarantine -- and then both proposers complete Phase 2 against the
    amnesiac acceptors and are active at the same instant.  This mirrors the TLC
    trace for counterexamples/LateTimer.tla.
    """

    def run() -> tuple[str, ...]:
        sim = Simulator(
            proposer_duration=4, acceptor_duration=4, quarantine=4, timer_at_quorum=True
        )
        sim.start_acquire("p1")
        sim.start_acquire("p2")
        for pid in ("p1", "p2"):
            for aid in ("a1", "a2"):
                sim.deliver_kind("prepare", dst=aid, src=pid)
        # The promise responses stay in flight while the acceptors crash,
        # forget them, restart, and wait out the FULL quarantine.
        for aid in ("a1", "a2"):
            sim.crash_acceptor(aid)
            sim.restart_acceptor(aid)
        sim.tick(4)
        # Under the step-3 rule each proposer's timer starts only now.
        for pid in ("p1", "p2"):
            for aid in ("a1", "a2"):
                sim.deliver_kind("promise", dst=pid, src=aid)
            for aid in ("a1", "a2"):
                sim.deliver_kind("accept", dst=aid, src=pid)
            for aid in ("a1", "a2"):
                sim.deliver_kind("accepted", dst=pid, src=aid)
        return ()

    return _expect_violation("late-promise-reuse", run)


def _stale_owner_open_schedule(sim: Simulator) -> None:
    """The shared schedule: p2 abandons an attempt with its accepts still in
    flight, p1 acquires under a lower ballot after crash, restart, and the
    FULL quarantine, the stale accepts overwrite p1's records, and p2
    retries, seeing "its own" lease reported everywhere."""
    # p2's first attempt: (1, 1, "p2"), which beats p1's (1, 1, "p1") on
    # the node tiebreak, mirroring a retrying proposer's higher ballot.
    sim.start_acquire("p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=aid, src="p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p2", src=aid)
    # The accept requests are now in flight; p2 gives up the attempt.
    sim.abandon("p2")
    for aid in ("a1", "a2"):
        sim.crash_acceptor(aid)
        sim.restart_acceptor(aid)
    sim.tick(2)  # the FULL quarantine is served
    # p1 acquires cleanly under its lower first ballot.
    sim.start_acquire("p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=aid, src="p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p1", src=aid)
    for aid in ("a1", "a2"):
        sim.deliver_kind("accept", dst=aid, src="p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("accepted", dst="p1", src=aid)
    assert "p1" in sim.active_owners()
    # The abandoned attempt's higher-ballot accepts land late, overwriting
    # p1's records with a stale p2-owned lease (ballot order permits it;
    # p1's authority is untouched, only its acceptor records are erased).
    for aid in ("a1", "a2"):
        sim.deliver_kind("accept", dst=aid, src="p2")
    # p2 retries with a fresh higher ballot and sees "its own" lease
    # reported by every acceptor.
    sim.start_acquire("p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=aid, src="p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p2", src=aid)


def stale_owner_open() -> CounterexampleResult:
    """Two owners when a proposer counts its own stale lease as open.

    Dropping P2's renewal qualifier (an own lease counts as open even while
    not active) lets a retrying proposer treat the record installed by its
    own abandoned attempt as permission.  Mirrors the 36-state TLC trace for
    counterexamples/StaleOwnerOpen.tla; both audited implementations carry
    the unqualified rule (StartProposing proceeds with a full fresh duration
    whenever the discovered lease owner is the node itself)."""

    def run() -> tuple[str, ...]:
        sim = Simulator(
            acceptor_ids=("a1", "a2"),
            proposer_duration=2,
            acceptor_duration=2,
            quarantine=2,
            self_open_when_inactive=True,
        )
        _stale_owner_open_schedule(sim)
        # The unqualified rule counted the stale own lease as open, so the
        # accept round completes and p2 activates beside p1.  Draining the
        # queue delivers p2's fresh accepts and their responses (the
        # abandoned attempt's stale responses are discarded by the ballot
        # check on the way).
        while sim.queue:
            sim.deliver(0)
        return ()

    return _expect_violation("stale-owner-open", run)


def split_brain_read_without_fence() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        p1_serves_read = True
        p2_commits_write = True
        ordered_by_log_or_fence = False
        assert not (p1_serves_read and p2_commits_write and not ordered_by_log_or_fence), (
            "unfenced read was concurrent with a newer owner write"
        )
        return ()

    return _expect_violation("split-brain-read-without-fence", run)


def suspended_event_loop() -> CounterexampleResult:
    def run() -> tuple[str, ...]:
        # The paired timely execution must NOT violate: the acquisition
        # timeout fires first and rotates the proposal identifier.
        run_timely_loop()
        return run_suspended_loop()

    return _expect_violation("suspended-event-loop", run)


def unsigned_expiry_underflow() -> CounterexampleResult:
    """The Phase 2 handlers in both audited systems read the clock once for
    the expiry guard and again for the activation-margin subtraction, with
    uint64_t deadlines (PLeaseProposer.cpp:124 and 144-145,
    PaxosLeaseProposer.cpp:114 and 129).  If the clock crosses the deadline
    between the two reads (a pause between the calls, or a forward step),
    the subtraction wraps and the margin check passes on an expired
    lease."""

    def run() -> tuple[str, ...]:
        u64 = 1 << 64
        expire_time = 8000
        # First read: the expiry guard passes with a millisecond to spare.
        now = 7999
        assert not (expire_time < now)
        # Second read: the clock has crossed the deadline in between.
        now = 8001
        remaining = (expire_time - now) % u64  # uint64_t arithmetic
        assert not (remaining > 500), (
            f"unsigned expiry subtraction underflowed to {remaining} and "
            "passed the activation margin after the expiry guard had "
            "already been cleared"
        )
        return ()

    return _expect_violation("unsigned-expiry-underflow", run)


COUNTEREXAMPLES = (
    insufficient_quarantine,
    owner_only_release,
    duplicate_quorum_counting,
    ballot_reuse_after_restart,
    skipped_paxos_recovery,
    unfenced_external_effect,
    nonintersecting_reconfiguration,
    unsafe_clock_source,
    renewal_without_quorum,
    stale_accept_overwrites_newer,
    late_promise_reuse,
    stale_owner_open,
    split_brain_read_without_fence,
    suspended_event_loop,
    unsigned_expiry_underflow,
)
