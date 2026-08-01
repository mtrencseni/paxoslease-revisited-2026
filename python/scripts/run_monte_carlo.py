from __future__ import annotations

import argparse

from paxoslease.monte_carlo import no_quarantine_counterexample, run_many

def main() -> None:
    parser = argparse.ArgumentParser(description="Run randomized PaxosLease simulator schedules.")
    parser.add_argument("--schedules", type=int, default=10_000)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260713)
    args = parser.parse_args()

    result = run_many(schedules=args.schedules, steps=args.steps, seed=args.seed)
    print(f"random schedules: {result.schedules}")
    print(f"steps per schedule: {result.steps_per_schedule}")
    print(f"total scheduler picks: {result.total_steps}")
    print(f"effective steps (state-changing): {result.effective_steps}")
    print(f"no-op picks (disabled operation chosen): {result.noop_steps}")
    print(f"seed: {result.seed}")
    print(f"max queued messages: {result.max_queue}")
    print(f"delivered messages: {result.delivered}")
    print(f"dropped messages: {result.dropped}")
    print(f"duplicated messages: {result.duplicated}")
    print(f"time advances: {result.ticks}")
    print(f"acceptor crashes: {result.acceptor_crashes}")
    print(f"  ... while a lease was active: {result.acceptor_crashes_while_lease_active}")
    print(f"acceptor restarts with messages in flight: {result.restarts_with_messages_in_flight}")
    print(f"proposer crashes: {result.proposer_crashes}")
    print(f"successful activations observed: {result.activations}")
    print("result: all checked schedules preserved invariants")

    violation = no_quarantine_counterexample()
    print(f"no-quarantine counterexample: {violation}")

if __name__ == "__main__":
    main()
