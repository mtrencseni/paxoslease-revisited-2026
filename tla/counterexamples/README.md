# Counterexample variants

These modules are full copies of `tla/spec/PaxosLease.tla` with exactly one rule
weakened. They are not sketches: TLC exhibits a `LeaseExclusivity` violation
for each under its `.cfg`, i.e. an execution with two simultaneously active
lease owners. Run them with `make counterexamples`.

- `LateTimer.tla`: the proposer starts its pending deadline when it receives
  a prepare quorum (step 3 of the pseudocode in the original 2012 PaxosLease
  paper) instead of when it sends `Prepare`. Nothing then bounds the age of a
  prepare quorum, so no finite quarantine makes acceptor restart safe: the
  configuration uses the full quarantine bound and TLC still finds a 27-state
  two-owner trace. The three-acceptor configuration (`LateTimer3.cfg` with
  the `LateTimerSym.tla` symmetry wrapper, `make counterexamples-3acceptors`)
  yields a 25-state trace in which a *single* crashed-and-restarted acceptor
  suffices; it explores ~151M distinct states and is not in the default
  targets.
- `OwnerOnlyRelease.tla`: a release message clears any lease of the same
  owner instead of the exact `(owner, ballot)` instance. A release delayed
  past a re-acquisition by the same owner erases the newer lease, and a
  second proposer acquires while the first is still active (36-state trace).
- `ScalarQuorumCounting.tla`: the proposer counts quorum responses by
  message instead of by distinct acceptor identity, under the base module's
  redelivering transport (`AllowRedeliver`). This is how both audited
  implementations count votes (scalar counters in Keyspace's
  `PLeaseProposer.cpp`, membership-check-only vote objects in ScalienDB's
  `MajorityQuorum.cpp`); it is sound only under at-most-once delivery per
  response, which their TCP transports provide by construction (pending
  writes are discarded on disconnect, nothing retransmits) but nothing
  documents. With redelivery allowed, a single acceptor's doubled response
  counts as a quorum and TLC finds an 18-state two-owner trace with no crash
  at all.
- `StaleOwnerOpen.tla`: the proposer counts a reported lease it owns as an
  open response even when it is not currently active (renewing), dropping
  rule P2's renewal qualifier. With retry enabled, an accept request left in
  flight by an abandoned attempt overwrites a competitor's live lease record
  and then, on the proposer's own retry, is read back as "its own" lease
  everywhere, licensing a fresh acquisition beside the still-active
  competitor. 36-state trace at the full quarantine bound, and no quarantine
  length prevents it. Both audited implementations carry the unqualified
  rule. Multi-hour search (`make counterexamples-staleowner`), recorded
  evidence rather than a default target.

A third failure mode needs no modified module: insufficient quarantine is a
configuration of the unmodified spec. `tla/spec/PaxosLeaseUnsafeQuarantine.cfg`
(durations 2/3) and `tla/spec/PaxosLeaseUnsafeQuarantine12.cfg` (durations 1/2)
set `Quarantine` one unit below `ProposerDuration`, one below the bound that
is tight in the checked model, and TLC finds 26- and 25-state two-owner
traces (`make unsafe-configs`).

The Python model mirrors the LateTimer failure as the `late-promise-reuse`
structured witness (`Simulator(timer_at_quorum=True)`), and
`tests/test_contracts.py` checks that the prepare-time rule blocks the exact
same schedule.
