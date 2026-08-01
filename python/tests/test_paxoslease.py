from __future__ import annotations


from hypothesis import given, settings, strategies as st

from paxoslease.messages import Message
from paxoslease.simulator import Simulator

def acquire(sim: Simulator, proposer: str, acceptors: tuple[str, ...] = ("a1", "a2")) -> None:
    sim.start_acquire(proposer)
    for aid in acceptors:
        sim.deliver_kind("prepare", dst=aid, src=proposer)
    for aid in acceptors:
        sim.deliver_kind("promise", dst=proposer, src=aid)
    for aid in acceptors:
        sim.deliver_kind("accept", dst=aid, src=proposer)
    for aid in acceptors:
        sim.deliver_kind("accepted", dst=proposer, src=aid)
    assert proposer in sim.active_owners()

def test_normal_acquisition_and_expiry() -> None:
    sim = Simulator(proposer_duration=3, acceptor_duration=3)
    acquire(sim, "p1")
    assert sim.active_owners() == {"p1"}
    sim.tick(2)
    assert sim.active_owners() == {"p1"}
    sim.tick(1)
    assert sim.active_owners() == set()

def test_preemption_prevents_lower_ballot_completion() -> None:
    sim = Simulator(proposer_duration=3, acceptor_duration=3)
    sim.start_acquire("p1")
    sim.deliver_kind("prepare", dst="a1", src="p1")
    sim.deliver_kind("promise", dst="p1", src="a1")

    sim.start_acquire("p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=aid, src="p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p2", src=aid)
    for aid in ("a1", "a2"):
        sim.deliver_kind("accept", dst=aid, src="p2")
    for aid in ("a1", "a2"):
        sim.deliver_kind("accepted", dst="p2", src=aid)

    assert sim.active_owners() == {"p2"}

def test_failed_renewal_does_not_extend_authority() -> None:
    sim = Simulator(proposer_duration=3, acceptor_duration=3)
    acquire(sim, "p1")
    old_deadline = sim.proposers["p1"].deadline

    sim.start_acquire("p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=aid, src="p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p1", src=aid)

    assert sim.proposers["p1"].deadline == old_deadline
    sim.tick(old_deadline - sim.now)
    assert "p1" not in sim.active_owners()

def test_stale_release_does_not_clear_renewed_instance() -> None:
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4)
    acquire(sim, "p1")
    old_ballot = sim.proposers["p1"].active_ballot
    stale = [Message("release", "p1", aid, ballot=old_ballot) for aid in sim.acceptor_ids]

    sim.start_acquire("p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("prepare", dst=aid, src="p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("promise", dst="p1", src=aid)
    for aid in ("a1", "a2"):
        sim.deliver_kind("accept", dst=aid, src="p1")
    for aid in ("a1", "a2"):
        sim.deliver_kind("accepted", dst="p1", src=aid)

    new_ballot = sim.proposers["p1"].active_ballot
    assert new_ballot != old_ballot
    sim.send(stale)
    for _ in stale:
        sim.deliver_kind("release")
    a1_accepted = sim.acceptors["a1"].accepted
    a2_accepted = sim.acceptors["a2"].accepted
    assert a1_accepted is not None and a1_accepted.ballot == new_ballot
    assert a2_accepted is not None and a2_accepted.ballot == new_ballot

def test_acceptor_restart_quarantine_blocks_forgotten_state_overlap() -> None:
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4)
    acquire(sim, "p1")
    sim.crash_acceptor("a1")
    sim.crash_acceptor("a2")
    sim.restart_acceptor("a1")
    sim.restart_acceptor("a2")

    sim.start_acquire("p2")
    sim.deliver_kind("prepare", dst="a1", src="p2")
    sim.deliver_kind("prepare", dst="a2", src="p2")
    sim.deliver_kind("prepare", dst="a3", src="p2")
    sim.deliver_kind("promise", dst="p2", src="a3")
    assert sim.active_owners() == {"p1"}
    assert sim.proposers["p2"].phase == "preparing"

    sim.tick(4)
    assert sim.active_owners() == set()

@given(st.lists(st.sampled_from([
    "start_p1", "start_p2", "deliver", "drop", "duplicate", "tick",
    "crash_a1", "restart_a1", "crash_p1", "restart_p1", "release_p1", "release_p2",
]), min_size=1, max_size=60))
@settings(max_examples=80, deadline=None)
def test_generated_schedules_preserve_safety(ops: list[str]) -> None:
    sim = Simulator(proposer_duration=3, acceptor_duration=3, quarantine=3)
    for op in ops:
        if op == "start_p1":
            sim.start_acquire("p1")
        elif op == "start_p2":
            sim.start_acquire("p2")
        elif op == "deliver" and sim.queue:
            sim.deliver(0)
        elif op == "drop" and sim.queue:
            sim.drop(0)
        elif op == "duplicate" and sim.queue:
            sim.duplicate(0)
        elif op == "tick":
            sim.tick(1)
        elif op == "crash_a1":
            sim.crash_acceptor("a1")
        elif op == "restart_a1":
            sim.restart_acceptor("a1")
        elif op == "crash_p1":
            sim.crash_proposer("p1")
        elif op == "restart_p1":
            sim.restart_proposer("p1")
        elif op == "release_p1":
            sim.release("p1")
        elif op == "release_p2":
            sim.release("p2")
        sim.check_safety()
