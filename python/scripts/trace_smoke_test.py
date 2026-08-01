from __future__ import annotations

from pathlib import Path

from paxoslease.simulator import Simulator
from paxoslease.trace import TraceRecorder

EXPECTED_EVENTS = {
    "StartAcquire",
    "DeliverPrepare",
    "DeliverPromise",
    "DeliverAccept",
    "DeliverAccepted",
}

def main() -> None:
    trace = TraceRecorder()
    sim = Simulator(proposer_duration=4, acceptor_duration=4, quarantine=4, trace=trace)
    sim.start_acquire("p1")
    while sim.queue:
        sim.deliver(0)
    events = {event.event for event in trace.events}
    missing = EXPECTED_EVENTS - events
    if missing:
        raise SystemExit(f"missing expected trace events: {sorted(missing)}")
    if not all(event.invariant_ok for event in trace.events):
        raise SystemExit("trace contains an invariant violation")
    if "p1" not in sim.active_owners():
        raise SystemExit("trace did not activate p1")
    out = Path(__file__).resolve().parents[2] / "results" / "trace-smoke-test.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        "trace smoke test passed (event schema + invariants on one happy-path acquisition; not TLA+ trace validation)\n"
        f"events: {', '.join(sorted(events))}\n"
        f"steps: {len(trace.events)}\n",
        encoding="utf-8",
    )
    print(out.read_text(), end="")

if __name__ == "__main__":
    main()
