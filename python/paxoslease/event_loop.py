"""Executable abstraction of the shipped event loop, and the
timer-dispatch-overrun violation it permits.

The audited implementations do not store an attempt deadline: freshness of a
lease attempt is enforced only by dispatch order, because the event loop runs
its timer scan before it polls for socket events (Keyspace
``src/System/Events/EventLoop.cpp``, ScalienDB
``src/System/Events/EventLoop.cpp``).  Anything that carries message
processing past a timer deadline before the next scan defeats that ordering;
a process suspension that begins after the last pre-deadline scan and ends
inside the poll is the dramatic instance reproduced here, but a socket
becoming ready just before the deadline, followed by a long enough handler
burst, produces the same schedule with no suspension at all.

This module reproduces the violating execution against a faithful
abstraction of the shipped node: proposer, acceptor, and learner colocated
in one process, exactly as deployed.  Colocation constrains the schedule,
because a node crash restarts every role at once and bumps the durable
restart counter spliced into the node's proposal identifiers
(counter-major ``(counter, restart, node_id)``, the layout built by
ReplicatedConfig::NextHighest).  A schedule in which a proposer-hosting
node crashes therefore cannot rely on that proposer keeping its old ballot
ordering.  The execution below respects this: the only node that crashes is
the single acceptor in the intersection of the two proposers' quorums, and
neither proposer's node ever restarts, so the node-identity tiebreak
between equal counters is legitimate.

The state machines mirror the sources:

  * ``start_preparing``   -- StartPreparing (fresh proposal identifier,
    acquisition timeout reset);
  * ``start_proposing``   -- StartProposing, where the lease timer starts:
    ``expireTime = Now() + duration`` (Keyspace PLeaseProposer.cpp:203,
    ScalienDB PaxosLeaseProposer.cpp:192);
  * ``on_propose_response`` -- the Phase 2 handler, which checks the lease
    expiry and the 500 ms activation margin but no attempt deadline,
    because none exists;
  * ``on_acquire_timeout`` -- the retry, which re-prepares with a fresh
    proposal identifier and thereby invalidates all responses to the old
    one;
  * ``Learner.on_learn_chosen`` -- the learner rule of both systems
    (PLeaseLearner.cpp, PaxosLeaseLearner.cpp): the owner itself installs
    the absolute local expiry it computed as proposer, while every other
    node re-anchors ``Now() + duration - 500`` at arrival.  Ownership is
    application-visible only through ``Learner.is_lease_owner()``, and the
    violation below is asserted at that level, not at the accepted-quorum
    level.

The violating schedule, in outline (times in ms, Keyspace constants):

  1. Node 2's proposer prepares ballot (1, 0, 2); the acceptors on nodes 1
     and 2 promise (quorum {1, 2}); the prepare to node 0 stays in flight.
  2. Node 1 alone crashes, forgetting its promise, restarts, and begins its
     full startup quarantine.  Nodes 0 and 2 never crash.
  3. Node 2's proposer receives the (delayed) promises and starts
     proposing: the lease timer starts NOW (the shipped rule); its accept
     requests are delayed in flight.  Its event loop performs the last
     timer scan before the retry deadline and blocks in the poll; the
     suspension begins there and outlasts node 1's quarantine.
  4. After node 1's quarantine, node 0's proposer completes an entire
     fresh acquisition with ballot (1, 0, 0) against quorum {0, 1}; its
     own learner installs the absolute expiry: node 0 is the
     application-visible master.
  5. The delayed accept requests for (1, 0, 2) now arrive: at node 1,
     (1,0,2) > (1,0,0) = promised, accepted; node 2's own acceptor accepts
     locally on resume.  When node 2 resumes inside the poll, the queued
     responses are dispatched before the overdue retry callback, the
     handler finds the lease expiry unreached with more than 500 ms
     remaining, the proposer activates, and its learner installs the
     absolute expiry: node 2 is also the application-visible master.

Two entry points: ``run_suspended_loop`` (the violation) and
``run_timely_loop`` (the identical schedule without the suspension: the
retry fires on time, rotates the identifier, and node 0 is the only
master).
"""

from __future__ import annotations

from dataclasses import dataclass, field

MAX_LEASE_TIME = 7000
ACQUIRELEASE_TIMEOUT = 2000
ACTIVATION_MARGIN = 500
LEARNER_HEDGE = 500
MAJORITY = 2  # 3 nodes


ProposalID = tuple[int, int, int]  # (counter, restart_counter, node_id)


@dataclass
class Acceptor:
    node_id: int
    promised: ProposalID | None = None
    accepted_owner: int | None = None
    accepted_ballot: ProposalID | None = None
    accepted_expire: int = 0
    quarantine_until: int = 0

    def crash(self) -> None:
        self.promised = None
        self.accepted_owner = None
        self.accepted_ballot = None
        self.accepted_expire = 0

    def restart(self, now: int) -> None:
        self.quarantine_until = now + MAX_LEASE_TIME

    def on_prepare(self, now: int, ballot: ProposalID) -> tuple[str, int | None]:
        assert now >= self.quarantine_until, "acceptor participated during quarantine"
        if self.promised is not None and ballot < self.promised:
            return ("rejected", None)
        self.promised = ballot
        if self.accepted_owner is not None and now < self.accepted_expire:
            return ("previously-accepted", self.accepted_owner)
        return ("open", None)

    def on_propose(self, now: int, ballot: ProposalID, owner: int) -> str:
        assert now >= self.quarantine_until, "acceptor participated during quarantine"
        if self.promised is not None and ballot < self.promised:
            return "rejected"
        self.promised = ballot
        self.accepted_owner = owner
        self.accepted_ballot = ballot
        self.accepted_expire = now + MAX_LEASE_TIME
        return "accepted"


@dataclass
class Learner:
    """The learner rule of PLeaseLearner.cpp / PaxosLeaseLearner.cpp: the
    owner installs its absolute local expiry; every other node re-anchors
    the remaining duration at arrival, minus a 500 ms hedge that is
    conservative only while delivery takes less than 500 ms."""

    node_id: int
    lease_owner: int | None = None
    expire_time: int = 0

    def on_learn_chosen(self, now: int, owner: int, duration: int, local_expire: int) -> None:
        if owner == self.node_id:
            expire = local_expire
        else:
            expire = now + duration - LEARNER_HEDGE
        if expire < now:
            return
        self.lease_owner = owner
        self.expire_time = expire

    def is_lease_owner(self, now: int) -> bool:
        return self.lease_owner == self.node_id and now < self.expire_time


@dataclass
class Proposer:
    node_id: int
    restart_counter: int = 0
    counter: int = 0
    preparing: bool = False
    proposing: bool = False
    proposal_id: ProposalID = (0, 0, 0)
    expire_time: int = 0
    ok_count: int = 0
    accept_count: int = 0
    acquire_timeout_at: int | None = None
    active_until: int = 0
    learner: Learner | None = None
    trace: list[str] = field(default_factory=list)

    def start_preparing(self, now: int) -> ProposalID:
        self.counter += 1
        self.proposal_id = (self.counter, self.restart_counter, self.node_id)
        self.preparing = True
        self.proposing = False
        self.ok_count = 0
        self.accept_count = 0
        self.acquire_timeout_at = now + ACQUIRELEASE_TIMEOUT
        self.trace.append(f"t={now} StartPreparing {self.proposal_id}")
        return self.proposal_id

    def on_promise(self, now: int, ballot: ProposalID, verdict: str) -> bool:
        """Returns True when this promise completes a prepare quorum."""
        if not self.preparing or ballot != self.proposal_id:
            return False
        if verdict != "open":
            return False
        self.ok_count += 1
        return self.ok_count >= MAJORITY

    def start_proposing(self, now: int) -> None:
        self.preparing = False
        self.proposing = True
        self.accept_count = 0
        # The shipped rule: the lease timer starts here, at prepare-quorum
        # receipt, not when Prepare was sent.
        self.expire_time = now + MAX_LEASE_TIME
        self.trace.append(f"t={now} StartProposing expire={self.expire_time}")

    def on_propose_response(self, now: int, ballot: ProposalID, verdict: str) -> None:
        # PLeaseProposer.cpp:124 -- only the lease expiry is checked; there
        # is no attempt deadline to check.
        if self.expire_time < now:
            return
        if not self.proposing or ballot != self.proposal_id:
            self.trace.append(f"t={now} stale response {ballot} dropped")
            return
        if verdict != "accepted":
            return
        self.accept_count += 1
        if self.accept_count >= MAJORITY and self.expire_time - now > ACTIVATION_MARGIN:
            self.proposing = False
            self.active_until = self.expire_time
            self.acquire_timeout_at = None  # EventLoop::Remove(&acquireLeaseTimeout)
            self.trace.append(f"t={now} ACTIVE until {self.active_until}")
            # LearnChosen: broadcast; delivered locally to the owner's own
            # learner in the same iteration.
            if self.learner is not None:
                self.learner.on_learn_chosen(
                    now, self.node_id, self.expire_time - now, self.expire_time
                )

    def run_timers(self, now: int) -> None:
        """The RunTimers half of an event-loop iteration."""
        if self.acquire_timeout_at is not None and now >= self.acquire_timeout_at:
            self.trace.append(f"t={now} OnAcquireLeaseTimeout")
            self.start_preparing(now)

    def is_active(self, now: int) -> bool:
        return now < self.active_until


def _schedule(suspended: bool) -> tuple[Learner, Learner, list[str]]:
    """The common schedule; ``suspended`` selects whether node 2's event
    loop pauses between its timer scan at t=1900 and its poll at t=7450.
    Quorums: the stale proposer (node 2) uses acceptors {1, 2}; the fresh
    proposer (node 0) uses acceptors {0, 1}.  Only node 1, the intersection,
    ever crashes, so no proposal identifier crosses a restart."""
    a0 = Acceptor(node_id=0)
    a1 = Acceptor(node_id=1)
    a2 = Acceptor(node_id=2)
    l0 = Learner(node_id=0)
    l2 = Learner(node_id=2)
    p_stale = Proposer(node_id=2, learner=l2)  # higher node id: wins the tiebreak
    p_fresh = Proposer(node_id=0, learner=l0)

    # t=0: node 2 prepares; nodes 1 and 2 promise; the prepare to node 0
    # stays in flight and is never delivered before node 0's own round.
    b_stale = p_stale.start_preparing(0)
    v1 = a1.on_prepare(100, b_stale)
    v2 = a2.on_prepare(100, b_stale)

    # t=200..300: node 1 alone crashes, right after promising, and
    # restarts; its startup quarantine runs to t=7300.  Nodes 0 and 2 never
    # crash, so neither proposer's restart counter moves.
    a1.crash()
    a1.restart(300)

    # t=1000: the delayed promises reach node 2's proposer, which starts
    # proposing: the lease timer starts NOW (expire 8000).  Its accept
    # requests to nodes 1 and 2 are delayed in flight.
    p_stale.on_promise(1000, b_stale, v1[0])
    if p_stale.on_promise(1000, b_stale, v2[0]):
        p_stale.start_proposing(1000)
    assert p_stale.proposing and p_stale.expire_time == 8000

    # t=1900: node 2's last timer scan before the acquisition timeout (due
    # t=2000).
    p_stale.run_timers(1900)
    if not suspended:
        # Timely dispatch: the next scan runs on time and the retry rotates
        # the proposal identifier.
        p_stale.run_timers(2000)

    # t=7310..7350: after node 1's quarantine, node 0's proposer runs a
    # complete fresh round against acceptors {0, 1}.  Its counter equals
    # node 2's, its restart counter is untouched (node 0 never crashed), so
    # its ballot is LOWER by the node-identity tiebreak.
    b_fresh = p_fresh.start_preparing(7310)
    assert b_fresh < b_stale, "tiebreak must make the fresh ballot lower"
    p_fresh.on_promise(7320, b_fresh, a0.on_prepare(7320, b_fresh)[0])
    if p_fresh.on_promise(7320, b_fresh, a1.on_prepare(7320, b_fresh)[0]):
        p_fresh.start_proposing(7330)
    p_fresh.on_propose_response(7340, b_fresh, a0.on_propose(7340, b_fresh, p_fresh.node_id))
    p_fresh.on_propose_response(7350, b_fresh, a1.on_propose(7350, b_fresh, p_fresh.node_id))
    assert l0.is_lease_owner(7360), "the fresh node must be the visible master"

    # t=7400: node 2's delayed accept requests arrive at node 1:
    # (1,0,2) > (1,0,0) = promised, so the amnesiac acceptor accepts and
    # overwrites; the response queues at node 2's socket.
    r1 = a1.on_propose(7400, b_stale, p_stale.node_id)

    # t=7450: node 2 resumes inside the poll.  The queued events are
    # dispatched before any timer scan: first its own acceptor processes
    # the local accept request (promised b_stale at t=100, never crashed),
    # then the proposer processes both responses.
    r2 = a2.on_propose(7450, b_stale, p_stale.node_id)
    p_stale.on_propose_response(7450, b_stale, r1)
    p_stale.on_propose_response(7450, b_stale, r2)

    log = p_stale.trace + p_fresh.trace
    return l0, l2, log


def run_suspended_loop() -> tuple[str, ...]:
    """The violating execution: the suspension lets the stale attempt
    activate, and two nodes are simultaneously application-visible masters
    through their learners."""
    l0, l2, log = _schedule(suspended=True)
    both = l0.is_lease_owner(7500) and l2.is_lease_owner(7500)
    assert not both, (
        "lease exclusivity violated during event-loop suspension: "
        f"node 0 master until {l0.expire_time}, node 2 master until {l2.expire_time}"
    )
    return tuple(log)


def run_timely_loop() -> tuple[str, ...]:
    """The same schedule without the suspension: the acquisition timeout
    fires on time, rotates the proposal identifier, and the stale responses
    are dropped."""
    l0, l2, log = _schedule(suspended=False)
    assert not l2.is_lease_owner(7500), "timely dispatch must drop the stale attempt"
    assert l0.is_lease_owner(7500), "the fresh node is the only visible master"
    return tuple(log)
