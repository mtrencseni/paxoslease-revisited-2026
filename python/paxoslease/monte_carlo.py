from __future__ import annotations

from dataclasses import dataclass
import random

from .simulator import Simulator


@dataclass(frozen=True)
class MonteCarloResult:
    schedules: int
    steps_per_schedule: int
    seed: int
    max_queue: int
    delivered: int
    dropped: int
    duplicated: int
    ticks: int
    acceptor_crashes: int
    proposer_crashes: int
    effective_steps: int
    noop_steps: int
    activations: int
    acceptor_crashes_while_lease_active: int
    restarts_with_messages_in_flight: int

    @property
    def total_steps(self) -> int:
        return self.schedules * self.steps_per_schedule


@dataclass
class _Counters:
    max_queue: int = 0
    delivered: int = 0
    dropped: int = 0
    duplicated: int = 0
    ticks: int = 0
    acceptor_crashes: int = 0
    proposer_crashes: int = 0
    effective: int = 0
    noop: int = 0
    activations: int = 0
    acceptor_crashes_while_lease_active: int = 0
    restarts_with_messages_in_flight: int = 0


# Delivery is weighted more heavily than the fault operations: with uniform
# choice almost no schedule completes an acquisition (eight in-order
# deliveries must beat the random ticks), so the interesting invariants --
# what happens to a LIVE lease under crashes, restarts, and stale messages --
# were barely exercised.
OPS = (
    "start",
    "release",
    "deliver",
    "deliver",
    "deliver",
    "deliver",
    "drop",
    "duplicate",
    "tick",
    "crash_acceptor",
    "restart_acceptor",
    "crash_proposer",
    "restart_proposer",
)


def _random_step(sim: Simulator, rng: random.Random, counters: _Counters) -> None:
    """One uniformly chosen operation.

    The scheduler picks operations blindly, so many picks are no-ops (deliver
    with an empty queue, restart of a running node, start of a busy
    proposer).  Every step classifies itself as effective or no-op so the
    recorded run reports meaningful transitions, not raw scheduler picks.
    """
    op = rng.choice(OPS)
    counters.max_queue = max(counters.max_queue, len(sim.queue))
    active_before = sim.active_owners()
    effective = False

    if op == "start":
        queue_before = len(sim.queue)
        sim.start_acquire(rng.choice(sim.proposer_ids))
        effective = len(sim.queue) > queue_before
    elif op == "release":
        queue_before = len(sim.queue)
        sim.release(rng.choice(sim.proposer_ids))
        effective = len(sim.queue) > queue_before
    elif op == "deliver":
        if sim.queue:
            sim.deliver(rng.randrange(len(sim.queue)))
            counters.delivered += 1
            effective = True
    elif op == "drop":
        if sim.queue:
            sim.drop(rng.randrange(len(sim.queue)))
            counters.dropped += 1
            effective = True
    elif op == "duplicate":
        if sim.queue:
            sim.duplicate(rng.randrange(len(sim.queue)))
            counters.duplicated += 1
            effective = True
    elif op == "tick":
        sim.tick(rng.randint(1, 2))
        counters.ticks += 1
        effective = True
    elif op == "crash_acceptor":
        aid = rng.choice(sim.acceptor_ids)
        effective = not sim.acceptors[aid].crashed
        sim.crash_acceptor(aid)
        if effective:
            counters.acceptor_crashes += 1
            if active_before:
                counters.acceptor_crashes_while_lease_active += 1
    elif op == "restart_acceptor":
        aid = rng.choice(sim.acceptor_ids)
        effective = sim.acceptors[aid].crashed
        sim.restart_acceptor(aid)
        if effective and sim.queue:
            counters.restarts_with_messages_in_flight += 1
    elif op == "crash_proposer":
        pid = rng.choice(sim.proposer_ids)
        effective = not sim.proposers[pid].crashed
        sim.crash_proposer(pid)
        if effective:
            counters.proposer_crashes += 1
    elif op == "restart_proposer":
        pid = rng.choice(sim.proposer_ids)
        effective = sim.proposers[pid].crashed
        sim.restart_proposer(pid)
    else:  # pragma: no cover
        raise AssertionError(op)

    counters.activations += len(sim.active_owners() - active_before)
    if effective:
        counters.effective += 1
    else:
        counters.noop += 1


def run_random_schedule(
    seed: int, steps: int, *, quarantine: int = 4, warm_start: bool = False
) -> _Counters:
    rng = random.Random(seed)
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=quarantine)
    counters = _Counters()
    if warm_start:
        # Half the schedules begin with a completed acquisition so the random
        # faults and stale messages exercise a live lease, not just idle state.
        acquire_on(sim, "p1")
        counters.activations += 1
    for _ in range(steps):
        _random_step(sim, rng, counters)
        sim.check_safety()
    counters.max_queue = max(counters.max_queue, len(sim.queue))
    return counters


def run_many(*, schedules: int, steps: int, seed: int = 20260713, quarantine: int = 4) -> MonteCarloResult:
    master = random.Random(seed)
    total = _Counters()
    for index in range(schedules):
        counters = run_random_schedule(
            master.randrange(2**63), steps, quarantine=quarantine, warm_start=index % 2 == 1
        )
        total.max_queue = max(total.max_queue, counters.max_queue)
        total.delivered += counters.delivered
        total.dropped += counters.dropped
        total.duplicated += counters.duplicated
        total.ticks += counters.ticks
        total.acceptor_crashes += counters.acceptor_crashes
        total.proposer_crashes += counters.proposer_crashes
        total.effective += counters.effective
        total.noop += counters.noop
        total.activations += counters.activations
        total.acceptor_crashes_while_lease_active += counters.acceptor_crashes_while_lease_active
        total.restarts_with_messages_in_flight += counters.restarts_with_messages_in_flight
    return MonteCarloResult(
        schedules=schedules,
        steps_per_schedule=steps,
        seed=seed,
        max_queue=total.max_queue,
        delivered=total.delivered,
        dropped=total.dropped,
        duplicated=total.duplicated,
        ticks=total.ticks,
        acceptor_crashes=total.acceptor_crashes,
        proposer_crashes=total.proposer_crashes,
        effective_steps=total.effective,
        noop_steps=total.noop,
        activations=total.activations,
        acceptor_crashes_while_lease_active=total.acceptor_crashes_while_lease_active,
        restarts_with_messages_in_flight=total.restarts_with_messages_in_flight,
    )


def acquire_on(sim: Simulator, proposer: str, acceptors: tuple[str, str] = ("a1", "a2")) -> None:
    sim.start_acquire(proposer)
    for acceptor in acceptors:
        sim.deliver_kind("prepare", dst=acceptor, src=proposer)
    for acceptor in acceptors:
        sim.deliver_kind("promise", dst=proposer, src=acceptor)
    for acceptor in acceptors:
        sim.deliver_kind("accept", dst=acceptor, src=proposer)
    for acceptor in acceptors:
        sim.deliver_kind("accepted", dst=proposer, src=acceptor)


def no_quarantine_counterexample() -> str:
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=0, unsafe=True)
    acquire_on(sim, "p1")
    for acceptor in ("a1", "a2"):
        sim.crash_acceptor(acceptor)
        sim.restart_acceptor(acceptor)

    sim.start_acquire("p2")
    for acceptor in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=acceptor, src="p2")
    for acceptor in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p2", src=acceptor)
    for acceptor in ("a1", "a2"):
        sim.deliver_kind("accept", dst=acceptor, src="p2")

    try:
        for acceptor in ("a1", "a2"):
            sim.deliver_kind("accepted", dst="p2", src=acceptor)
    except AssertionError as exc:
        return str(exc)
    raise AssertionError("no-quarantine counterexample did not violate an invariant")
