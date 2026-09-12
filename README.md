# PaxosLease

This repository contains a LaTeX paper, executable TLA+ models, TLAPS support obligations, deterministic Python reference models, negative witnesses, and recorded verification outputs for:

**PaxosLease Revisited: A Checked Model of Diskless Distributed Leases**

The paper is `paper/PaxosLease-Revisited.pdf`; its source is `paper/PaxosLease-Revisited.tex`.

## Central question

Under what exact conditions can a quorum-based lease protocol safely discard all acceptor lease state after a crash?

The checked model's answer is that a restarted acceptor must refuse all lease-layer participation until every forgotten lease and every forgotten prepare response is no longer able to affect an active proposer. Under the prepare-time timer rule everything an acceptor can forget belongs to an attempt whose Prepare preceded the crash, so in the discrete model:

```text
Quarantine >= ProposerDuration
```

The bound tracks the proposer attempt duration, not the acceptor exclusion duration. The Python timing helper generalizes this to bounded elapsed-clock rates and an operation margin.

## Findings about the original 2012 paper

- **The pseudocode's timer rule is unsafe.** The 2012 paper is internally
  inconsistent: its Figure 2 starts the proposer's timer before the prepare
  requests, its step-3 pseudocode starts it at prepare-quorum receipt. Under
  the pseudocode rule the attempt has no deadline yet, so arbitrarily old
  prepare responses stay usable, and TLC
  exhibits two simultaneous lease owners even with the full quarantine
  (`tla/counterexamples/LateTimer.tla`, 27-state trace). The safe rule, starting
  the pending deadline when `Prepare` is sent, is the one the figure draws
  and the one this model adopts.
- **The quarantine bound is tight in the checked model, and it is
  `Quarantine >= Dp`, not `max(Dp, Da)`.** With the prepare-time timer rule, quarantine equal to the
  proposer duration and strictly below the acceptor duration passes an
  exhaustive two-proposer crash/restart check
  (`tla/spec/PaxosLeaseQuarantineEqualsProposer.cfg`, 20,447,948 distinct states), and
  one unit below the proposer duration TLC exhibits two owners
  (`tla/spec/PaxosLeaseUnsafeQuarantine.cfg`). The separated-duration experiment refutes the
  `max(D_P, D_A)` bound by ruling out its acceptor half.

## Reproduce

Use a Python virtual environment. The `venv` target installs this repository as an editable package, so tests and scripts import `paxoslease` without modifying `PYTHONPATH`.

```sh
make venv
make paper-evidence
```

`paper-evidence` is the fail-fast target: it re-runs every result the paper
cites except the long searches, whose recorded outputs under
`results/` it instead validates against the paper's cited trace lengths and
state counts (`python/scripts/check_paper_claims.py`, target `paper-claims`).
`make paper-evidence-full` re-runs the long searches too. `make results`
regenerates the recorded report `results/verification-results.md`, and
`make all` builds everything including the PDF.

Useful partial targets:

```sh
make pdf
make parse
make lint
make check-standalone
make check-composition
make counterexamples
make unsafe-configs
make prove
make test
make monte-carlo
make expected-counterexamples
make variant-check
make trace-smoke-test
make timing-examples
```

The TLA+ wrappers expected on this machine are `sany`, `tlc`, and `tlapm`. Do not install TLA+ tooling or call `java -jar` directly for normal work in this repository.

## Project map

| Path | Contents |
|---|---|
| `paper/` | The paper: `PaxosLease-Revisited.tex` and the built `.pdf`. |
| `tla/spec/` | Executable TLA+ models and TLC configurations. |
| `tla/counterexamples/` | Intentionally weakened variants; TLC finds a two-owner trace for each. |
| `tla/proof/` | TLAPS support-obligation module. |
| `python/paxoslease/` | Executable reference model: simulator, composed PaxosLease/Paxos model, timing, tracing, fencing, and the structured witnesses. |
| `python/demo.py` | Single-file runnable demonstration: correct PaxosLease on real timers, three nodes in one event loop. Reading material, not evidence. |
| `python/tests/` | Scenario tests, property tests, and contract tests. |
| `python/scripts/` | Verification pipeline: claim checking, variant generation, recording. |
| `results/` | Recorded outputs from checks and experiments. |
| `docs/implementation-contract.md` | The protocol/implementation assumptions and evidence boundary. |
| `docs/tooling-instructions.md` | Installing Java, the TLA+ tools, TLAPS, and Python. |
| `build/` | Everything the tools generate. Disposable; `make clean` removes it. |

## Evidence boundary

| Claim type | Repository evidence |
|---|---|
| Finite-state protocol safety | TLC configurations in `tla/spec/`. |
| Arithmetic/proof support | TLAPS obligations in `tla/proof/`. |
| Implementation behavior | Python scenario/property/randomized tests. |
| Unsafe variants | TLA+ counterexamples and `results/counterexamples.json`. |
| Paxos composition | Abstract TLA+ model and deterministic Python admission/recovery model. |

The repository does not claim a complete parameterized TLAPS proof, a production Paxos implementation, or a full reconfiguration protocol. Those boundaries are stated explicitly in the paper and in `docs/implementation-contract.md`.
