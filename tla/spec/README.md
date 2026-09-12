# PaxosLease specification notes

This directory contains the executable TLA+ models used by the paper.

## Chosen protocol semantics

- A lease instance is identified by `(owner, ballot)`; release messages match the exact ballot and owner.
- Expiration is interpreted by `now < deadline`, not by assuming timer callbacks run exactly on time.
- Expired accepted state may remain stored, but prepare responses report it as empty.
- Acceptor promises are volatile in this model and are lost on crash with the rest of PaxosLease state.
- The TLA+ composition abstracts Paxos agreement and checks admission; it declares no Paxos acceptors.  The Python composition models ballot-checking durable Paxos acceptors.
- A proposer starts its pending local countdown when it sends `Prepare` (the prepare-time timer rule). Starting it later, at prepare-quorum receipt as in the original 2012 pseudocode, is unsafe: see `tla/counterexamples/LateTimer.tla`.
- A proposer becomes active only after a quorum of `Accepted` responses and before its pending deadline expires.
- `cert` and `certDeadline` are history (ghost) variables used to state invariants; the protocol never compares deadlines across processes.
- Renewal uses a fresh ballot and the same two phases; a failed renewal does not extend authority.
- A proposer may abandon a non-idle attempt (`AbandonAttempt`, gated by `AllowAbandon`) and retry with a fresh, higher ballot; abandoning keeps the proposer alive and keeps any lease it holds, unlike crash/restart. `PaxosLeaseRetry.cfg` checks explicit retries with the abandoned attempt's messages still in the network, across acceptor crash and restart at the quarantine boundary (exhaustive but very large, so it is recorded evidence: `make check-retry`, output in `results/retry.txt`, validated against the paper by `make paper-claims`, re-run by `make paper-evidence-full`).
- A reported lease the proposer owns counts as an open prepare response only while the proposer is currently active AND the reported instance is that exact lease being renewed (its ballot equals the active ballot): P2's renewal qualifier, stated as provenance. Unqualified, the rule is unsafe under retry: an abandoned attempt's accept can overwrite a competitor's record and then license its sender's fresh acquisition. See `tla/counterexamples/StaleOwnerOpen.tla` (36-state two-owner trace at the full quarantine; `make counterexamples-staleowner`, multi-hour). Both audited implementations implement the unqualified rule.
- The acceptor-side repair is checked too: with `RefuseLiveOverwrite`, an acceptor never replaces a live lease of a different owner (A2 refuses like a ballot rejection). Alone, with the renewal qualifier deliberately dropped, it passes the retry configuration exhaustively (`make staleowner-a2`, 337,917,446 distinct states, recorded in `results/staleowner-a2.txt`).
- Transport realizability is a refinement, not an argument: with `CrashDropsIncoming`, messages addressed to a process are discarded both at its crash and at its restart, so every delivered message was provably sent after its addressee's most recent restart (connection-lifecycle delivery; messages already sent by a crashed process survive). Every trap survives the refinement at unchanged trace depths: LateTimer 27 states (stale promises are sent by the crashing acceptors), StaleOwnerOpen 36 states (the recorded trace sends the stale accepts after the restart, on fresh connections), the implementation projection's delayed-dispatch execution 27 states and its colocated form 25 states. The stale-owner composition is also checked inside the implementation projection: `PaxosLeaseImplStaleOwner.cfg` (shipped timely constants, three ballots, connection lifecycle) yields a 35-state two-owner execution after 564,425,413 distinct states (`make impl-staleowner`). `make transport-refinement` runs the fast pair; the multi-hour forms are recorded.
- A proposer crash immediately removes lease authority.
- A restarted acceptor enters quarantine for `Quarantine`, during which it sends no promise, accept, or release response.
- The network is a set: identical concurrent sends collapse, and delivery normally consumes the message, so the default transport is at-most-once by construction. With `AllowRedeliver` every deliver action may nondeterministically leave the message in the network, so the same request or response can be delivered again arbitrarily later. `PaxosLeaseRedeliver.cfg` (no crashes, fail-fast in `make check-standalone`) checks that duplicated requests and responses cannot manufacture a quorum because responses are counted by distinct acceptor identity, and `PaxosLeaseRedeliverCrash.cfg` (crash and restart at the quarantine boundary; exhaustive but very large, recorded via `make check-redeliver-crash` into `results/redeliver-crash.txt`) checks the same transport against forgetting. Counting by message instead is safe only under at-most-once delivery per response: see `tla/counterexamples/ScalarQuorumCounting.tla`, which runs scalar counting under `AllowRedeliver = TRUE`.

## The implemented protocol (`PaxosLeaseImpl.tla`)

`PaxosLeaseImpl.tla` is a standalone model of the protocol the audited
production systems (Keyspace, ScalienDB) actually run, differing from the
base specification in exactly two rules taken from their sources: the lease
timer starts at prepare-quorum receipt (the 2012 pseudocode's step-3 rule),
and an attempt timeout of `RetryTimeout` units, armed at `Prepare`, abandons
the ballot when it fires. The constant `TimelyDispatch` selects whether the
timeout callback runs as soon as it is due (an event loop that is never
paused) or may be delayed past message processing (a process suspension).
Seven configurations; the first six run by `make check-impl`, the colocation-valid one by `make check-impl-colocated`:

- `PaxosLeaseImplTimelyShipped.cfg`: shipped ordering of the constants,
  `(D_P, R, Q) = (2, 1, 2)`: passes exhaustively under timely dispatch.
- `PaxosLeaseImplTimelyBoundary.cfg`: `(D_P, R, Q) = (2, 2, 2)`, the
  boundary of `Quarantine >= max(ProposerDuration, RetryTimeout)`.
- `PaxosLeaseImplTimelyRDominantSafe.cfg`: `(D_P, R, Q) = (1, 2, 2)`,
  quarantine covering a retry timeout that exceeds the attempt duration.
- `PaxosLeaseImplTimelyBelow.cfg`: quarantine one unit below the attempt
  duration: two-owner trace (26 states).
- `PaxosLeaseImplTimelyRDominant.cfg`: retry timeout exceeding the
  quarantine: two-owner trace (26 states), so the undocumented shipped
  condition `R <= M` is necessary for safety (the boundary `R = M`
  passes, so the condition is non-strict).
- `PaxosLeaseImplDelayedShipped.cfg`: shipped constants, delayed dispatch:
  two-owner trace (27 states), the timer-dispatch-overrun execution.
- `PaxosLeaseImplDelayedColocated.cfg`: the colocation-valid form: three
  acceptors, and the module's `CrashableAcceptors` constant restricted to
  the single acceptor in the intersection of the two proposers' quorums.
  In the deployed systems proposer and acceptor are colocated and a node
  crash bumps the restart counter inside that node's proposal identifiers;
  in any trace this configuration finds, no proposer-hosting node crashes,
  so the trace is valid for the colocated deployment without modeling
  restart counters. Violated: 25-state two-owner trace, found after
  exploring 262,728,880 distinct states (`make check-impl-colocated`,
  multi-hour).

## Timing assumptions

Safe configurations require:

```text
ProposerDuration <= AcceptorDuration   (timer containment)
Quarantine >= ProposerDuration         (safe forgetting)
```

The quarantine bound tracks the proposer attempt duration, not the acceptor
exclusion duration: under the prepare-time timer rule, everything an acceptor
can forget belongs to an attempt whose Prepare preceded the crash, and that
attempt expires `ProposerDuration` later.
`PaxosLeaseQuarantineEqualsProposer.cfg` (durations 1/2) and
`PaxosLeaseQuarantineEqualsProposer23.cfg` (durations 2/3) check the separated
boundary `Quarantine = ProposerDuration < AcceptorDuration` exhaustively.

`PaxosLease.tla` itself assumes only the containment condition. The quarantine
bound lives in `PaxosLeaseChecked.tla`, a thin wrapper that safe
configurations check. This split lets TLC *exhibit* the two-owner execution
when the bound is violated instead of rejecting the configuration:
`PaxosLeaseUnsafeQuarantine.cfg` (durations 2/3, quarantine 1) and
`PaxosLeaseUnsafeQuarantine12.cfg` (durations 1/2, quarantine 0) run the raw
module with `Quarantine` one unit below `ProposerDuration` and
`make unsafe-configs` requires TLC to find the `LeaseExclusivity` violation
in each. `PaxosLeaseUnsafeQuarantine3.cfg` with the `PaxosLeaseSym.tla`
symmetry wrapper is the three-acceptor version (24-state trace, ~167M states
explored; run on demand, recorded in `results/unsafe-config-3acceptors.txt`). `PaxosLeaseCrashRestart.cfg` additionally
checks two proposers racing across acceptor crash and restart with equal
durations.

## Invariant inventory

| Item | Status | Representation | Checked by |
|---|---|---|---|
| Type correctness | direct invariant | `TypeOK` | TLC |
| Accepted-state coherence | direct invariant | `AcceptedCoherence` | TLC |
| Activation has quorum | direct invariant with history | `ActivationHasQuorum`, `cert` | TLC |
| Timer containment | direct invariant with history | `TimerContainment`, `certDeadline` | TLC |
| Active implies unexpired | direct invariant | `ActiveImpliesUnexpired` | TLC |
| Lease exclusivity | direct invariant | `LeaseExclusivity` | TLC |
| Release matches instance | action rule + counterexample | `DeliverRelease`, `OwnerOnlyRelease.tla` | TLC |
| Failed renewal grants no extension | transition rule + tests | pending deadline only committed on quorum | TLC/tests |
| Quarantine prevents participation | direct invariant and action guards | `QuarantinePreventsParticipation`, `CanParticipateA` | TLC |
| Safe forgetting | derived argument | quarantine duration + timer containment | hand/TLC |
| Quorum intersection | assumption for fixed majority quorums | `IsQuorum` | definition/TLC |
| Chosen-value well-formedness | by construction in the abstraction | `ChosenValueWellFormed` | TLC |
| Ready implies active | direct invariant | `ReadyImpliesActive` | TLC |
| Ready-leader uniqueness | direct invariant | `ReadyLeaderUniqueness` | TLC |
| Recovery precedes admission | direct invariant | `RecoveryPrecedesAdmission` | TLC |
| Ready implies recovered (per epoch) | direct invariant | `ReadyImpliesRecovered` | TLC |
| Log-prefix consistency | abstract invariant | `LogPrefixConsistency` | TLC |

## Evidence boundary

The TLC models are finite. They check the exact constants in each `.cfg` file. The TLAPS module in `tla/proof/` is a support-obligation artifact, not a complete parameterized proof of the full transition system.
