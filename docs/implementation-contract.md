# PaxosLease implementation contract

This document states what the executable models in this repository require from an implementation. It is intentionally stricter than the informal protocol sketch: every item below is either checked directly, represented by a negative example, or marked as outside the current proof boundary.

## Safety question

The central question is:

> Under what exact conditions can a quorum-based lease protocol safely discard all acceptor lease state after a crash?

The answer modeled here is: an acceptor may discard volatile PaxosLease state only if, after restart, it refuses all lease-layer participation until every lease or prepare response that it might have forgotten is unable to affect an active owner. Under the prepare-time timer rule, everything an acceptor can forget belongs to a proposer attempt whose Prepare preceded the crash, and that attempt is unusable one proposer duration later. In the discrete model this is captured by:

```text
Quarantine >= ProposerDuration
```

The bound tracks the proposer attempt duration, not the acceptor exclusion duration: TLC passes exhaustively with `Quarantine = ProposerDuration < AcceptorDuration` and violates lease exclusivity one unit below (an earlier draft of this contract claimed `max(ProposerDuration, AcceptorDuration)`; the separated-duration model-checking experiment refuted the acceptor half). The Python timing layer generalizes the bound to bounded local clock-rate error and operation margin. Note that the bound depends on the prepare-time timer rule; with the 2012 paper's step-3 rule no finite quarantine suffices.

## Required protocol rules

| Rule | Status | Evidence |
|---|---|---|
| Quorums must intersect. | Assumption for majority configs. | TLA definitions, Python quorum checks, `nonintersecting-reconfiguration` witness. |
| A proposer is active only after an accepted quorum. | Direct model rule. | TLC invariants, Python simulator checks. |
| Quorum responses are counted by distinct acceptor id, or the transport guarantees at-most-once delivery per response. | Direct model rule. | `duplicate-quorum-counting` witness; `tla/spec/PaxosLeaseRedeliver.cfg` checks identity counting safe under the base module's redelivering transport (`AllowRedeliver`); TLC trace for `tla/counterexamples/ScalarQuorumCounting.tla` (18 states, no crash) shows scalar counting unsafe under the same transport. Both audited implementations count scalars; in the audited sources no redelivery path was found (pending writes are discarded on disconnect), but at-most-once delivery is an undocumented accident there, not a stated guarantee, and a complete proof of the transport was not performed. |
| A lease instance is identified by owner and ballot. | Direct model rule. | exact release logic, `owner-only-release` witness, TLC trace for `tla/counterexamples/OwnerOnlyRelease.tla`. |
| Acceptors reject lower ballots after promising higher ballots. | Direct model rule. | TLC checks, `stale-accept-overwrites-newer` witness. |
| A renewal extends authority only after a fresh accept quorum. | Direct model rule. | scenario tests, `renewal-without-quorum` witness. |
| The attempt deadline starts when Prepare is sent, so prepare responses expire with the attempt that collected them. | Direct model rule. | prepare-time pending deadline; `late-promise-reuse` witness and TLC trace for `tla/counterexamples/LateTimer.tla` show the step-3 timer rule of the 2012 paper is unsafe. |
| A reported lease the proposer owns is an open prepare response only while the proposer is currently active AND the reported instance is the lease being renewed (ballot match); otherwise it blocks like a foreign lease. Alternatively (or additionally, as defense in depth), the acceptor never replaces a live lease of a different owner. | Direct model rule (P2's renewal qualifier; A2's `RefuseLiveOverwrite`). | `stale-owner-open` witness; TLC trace for `tla/counterexamples/StaleOwnerOpen.tla` (36 states, full quarantine, retry enabled); the acceptor-side repair alone passes exhaustively (`results/staleowner-a2.txt`). The execution survives the connection-lifecycle transport refinement (`CrashDropsIncoming`, purging at crash and at restart; the recorded trace sends the stale accepts after the restart), so connection teardown does not mask it, and the checked implementation projection composes the two shipped mechanisms into the same execution under shipped timely constants (`results/impl-staleowner.txt`, 35 states). Both audited implementations carry the unqualified rule: `StartProposing` proceeds with a full fresh duration whenever the discovered lease owner is the node itself (keyspace `PLeaseProposer.cpp`, scaliendb `PaxosLeaseProposer.cpp`), so their retry timeout can convert an abandoned attempt's stale accept into a second owner. |
| The attempt time bound is enforced as stored protocol state checked in the response handlers, not as timer dispatch order. | Direct model rule. | `suspended-event-loop` witness (executable colocated-node abstraction of the shipped iteration order, asserted at learner level); `tla/spec/PaxosLeaseImpl.tla` under delayed dispatch, TLC two-owner traces with the shipped constants, including the colocation-valid `PaxosLeaseImplDelayedColocated.cfg`. |
| Expiry comparisons read the clock once per handler and compare before subtracting; deadline arithmetic must not be exposed to unsigned wraparound. | Contract rule from the audit. | `unsigned-expiry-underflow` witness; both audited Phase 2 handlers read the clock twice on `uint64_t` deadlines. |
| The acting owner's learner preserves the proposer's absolute deadline; remote learners that re-anchor durations at arrival must state their delivery-delay bound. | Contract rule from the audit. | Both audited learners preserve the absolute deadline for the owner and re-anchor with an undocumented 500 ms hedge for remote nodes. |
| Restarted acceptors ignore prepare, accept, and release while quarantined. | Direct model rule. | Python contract test and TLC guards. |
| Proposer restart cannot reuse a ballot. | Python rule. | epoch ballot test, `ballot-reuse-after-restart` witness. |
| Paxos client admission requires Paxos recovery after lease acquisition. | Composition rule. | composed Python model, TLC abstraction, `skipped-paxos-recovery` witness. |
| External side effects require fencing or log ordering. | Contract rule. | `FencedResource`, `unfenced-external-effect`, `split-brain-read-without-fence`. |
| Reconfiguration preserves quorum intersection or waits out old leases. | Open design rule. | documented; negative witness only. |

## Timing contract

The model assumes local elapsed-time measurements, not synchronized clocks. The Python helper uses bounds

```text
r_min * real_elapsed <= local_elapsed <= r_max * real_elapsed
```

for every live timer. A safe acceptor exclusion must outlast the proposer's usable interval in real time. A safe quarantine must outlast, in real time, the proposer attempt interval; forgotten acceptor exclusions matter only through the attempts they support.

Unsafe time sources include wall clocks that can step backward, timers that pause during suspend without treating the process as failed, and virtualized clocks whose rate bounds are unknown. The repository treats those cases as outside the implementation contract unless the runtime can re-establish the same elapsed-time bounds.

## Evidence labels

| Label | Meaning in this repository |
|---|---|
| TLC-checked | A finite TLA+ configuration was exhaustively model checked. |
| TLAPS-support | A formula-level support obligation was machine checked. |
| Python-tested | Deterministic scenarios, property tests, or randomized schedules exercised the executable model. |
| Counterexample-backed | A deliberately broken rule has a reproducible witness. |
| Informal | The argument is written in the paper but is not fully mechanized. |
| Open | The paper states the required condition but does not implement a full model. |

## What is not claimed

The repository does not contain a complete parameterized TLAPS proof of PaxosLease. It does not contain a full production Multi-Paxos implementation. The composed Paxos model is an admission and recovery model meant to check that PaxosLease does not remove the need for Paxos recovery. Reconfiguration is not implemented as a full protocol; the contract states the necessary intersection/wait-out condition and includes a negative witness for the unsafe case.
