"""Cross-check the paper's cited numbers against the recorded results.

Every number the paper cites that a recorded artifact can confirm is listed
here and checked mechanically: violation trace lengths against the recorded
TLC trace files, exhaustive distinct-state counts against
results/verification-results.md, and the large recorded searches against
their recorded output files.  A mismatch means either the paper or the
recorded evidence drifted; the target fails until they agree again.

Two kinds of cited numbers are deliberately NOT checked.  Explored-state
counts of regenerated violation runs are nondeterministic (parallel TLC
stops wherever a worker first finds the violation), so the paper cites only
the stable minimum-depth trace lengths for those.  The MaxNetwork
sensitivity counts in Appendix D came from one-off manual
runs and are not part of the recorded pipeline.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "paper" / "PaxosLease-Revisited.tex"
RESULTS = ROOT / "results"
MD = RESULTS / "verification-results.md"

# Violation results files: each must record the LeaseExclusivity violation
# and a trace of exactly this length (BFS minimal depth, stable across runs).
TRACE_EXPECTATIONS: dict[str, int] = {
    "counterexample-latetimer.txt": 27,
    "counterexample-latetimer-3acceptors.txt": 25,
    "counterexample-owneronlyrelease.txt": 36,
    "counterexample-scalarquorumcounting.txt": 18,
    "impl-timely-below.txt": 26,
    "impl-timely-rdominant.txt": 26,
    "impl-delayed-shipped.txt": 27,
    "impl-delayed-colocated.txt": 25,
    "unsafe-config-3acceptors.txt": 24,
    "counterexample-staleowneropen.txt": 36,
    # Transport-realizability refinement (CrashDropsIncoming = TRUE): every
    # trap survives connection semantics, at unchanged trace depths.
    "counterexample-latetimer-tcp.txt": 27,
    "staleowner-tcp.txt": 36,
    "impl-delayed-shipped-tcp.txt": 27,
    "impl-delayed-colocated-tcp.txt": 25,
    # The stale-owner composition inside the implementation projection:
    # shipped timely constants, three ballots, connection lifecycle.
    "impl-staleowner.txt": 35,
}

# Most violation runs check LeaseExclusivity directly; the implementation
# stale-owner configuration checks the Safety conjunction, and TLC names
# the conjunction in its violation line.
VIOLATED_INVARIANT: dict[str, str] = {
    "impl-staleowner.txt": "Invariant Safety is violated",
}
DEFAULT_VIOLATION = "Invariant LeaseExclusivity is violated"

# Recorded long searches: the paper or spec/README.md cites the
# distinct-state count of the recorded run, so the recorded file must
# contain exactly that count.
RECORDED_DISTINCT: dict[str, int] = {
    "counterexample-latetimer-3acceptors.txt": 151_146_929,
    "impl-delayed-colocated.txt": 262_728_880,
    "unsafe-config-3acceptors.txt": 167_062_618,
    "retry.txt": 251_904_392,
    # The A2 repair alone (renewal qualifier deliberately dropped) passes
    # the retry configuration exhaustively.
    "staleowner-a2.txt": 337_917_446,
    # Interaction configurations and the MaxNetwork sensitivity run.
    "renew-retry.txt": 280_165_306,
    "retry-redeliver.txt": 53_723_103,
    "renew-release-stale.txt": 204_050,
    "retry-mn5.txt": 465_991_204,
    "impl-delayed-colocated-tcp.txt": 284_288_181,
    "impl-staleowner.txt": 564_425_413,
}

# Exhaustive distinct-state counts of passing configurations: deterministic,
# cited in the paper's tables, regenerated into verification-results.md.
MD_DISTINCT: list[int] = [
    573_975,      # Base
    7_717,        # Renew/release
    10_059_404,   # Crash/restart
    19_656,       # Drift
    20_447_948,   # Quarantine = D_P (1,2,1)
    9_867_548,    # Quarantine = D_P (2,3,2)
    1_857_563,    # Redeliver (no crash)
    2_095,        # Lease+Paxos composition
    37_160_904,   # Impl timely boundary (2,2,2)
    37_476_080,   # Impl timely R-dominant safe (1,2,2)
    18_160_464,   # Impl timely shipped (2,1,2)
]

# Each number above, as the paper writes it.  The tex is normalized by
# replacing "{,}" with "," before searching.
TEX_SNIPPETS: list[str] = [
    "27 states",
    "36 states",
    "18 states",
    "26 states",
    "25-state trace",
    "27-state trace",
    "25-state two-owner trace",
    "24-state trace",
    "573,975",
    "7,717",
    "10,059,404",
    "19,656",
    "20,447,948",
    "9,867,548",
    "1,857,563",
    "2,095",
    "37,160,904",
    "37,476,080",
    "18,160,464",
    "151,146,929",
    "262,728,880",
    "251,904,392",
    "337,917,446",
    "280,165,306",
    "53,723,103",
    "204,050",
    "465,991,204",
    "284,288,181",
    "564,425,413",
    "35-state",
]


def trace_length(text: str) -> int:
    return len(re.findall(r"^State \d+", text, flags=re.MULTILINE))


def main() -> None:
    failures: list[str] = []

    tex = TEX.read_text(encoding="utf-8").replace("{,}", ",")
    md = MD.read_text(encoding="utf-8")

    for name, expected_len in TRACE_EXPECTATIONS.items():
        path = RESULTS / name
        if not path.exists():
            failures.append(f"{name}: recorded results file missing")
            continue
        text = path.read_text(encoding="utf-8")
        expected_violation = VIOLATED_INVARIANT.get(name, DEFAULT_VIOLATION)
        if expected_violation not in text:
            failures.append(f"{name}: expected '{expected_violation}' not recorded")
        got = trace_length(text)
        if got != expected_len:
            failures.append(f"{name}: trace length {got}, paper cites {expected_len}")

    for name, distinct in RECORDED_DISTINCT.items():
        path = RESULTS / name
        if not path.exists():
            continue  # already reported above
        text = path.read_text(encoding="utf-8")
        if not re.search(rf"\b{distinct} distinct states found\b", text):
            failures.append(f"{name}: recorded run does not show {distinct} distinct states")

    for distinct in MD_DISTINCT:
        if not re.search(rf"\b{distinct} distinct states found\b", md):
            failures.append(
                f"verification-results.md: missing exhaustive count {distinct}"
            )

    for snippet in TEX_SNIPPETS:
        if snippet not in tex:
            failures.append(f"paper: cited number or phrase not found: {snippet!r}")

    # The witness count the paper states in words must match the recorded
    # witness registry.
    witnesses = json.loads((RESULTS / "counterexamples.json").read_text(encoding="utf-8"))
    count_words = {13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen"}
    word = count_words.get(len(witnesses))
    if word is None:
        failures.append(f"witness registry has unmapped count {len(witnesses)}")
    elif f"{word} structured" not in tex:
        failures.append(
            f"paper: witness count mismatch: registry has {len(witnesses)} "
            f"({word}), but '{word} structured' not found in the tex"
        )
    for stale_word in count_words.values():
        if stale_word != word and f"{stale_word} structured" in tex:
            failures.append(f"paper: stale witness count '{stale_word} structured' present")

    if failures:
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        sys.exit(1)
    print(
        f"paper claims consistent: {len(TRACE_EXPECTATIONS)} traces, "
        f"{len(RECORDED_DISTINCT)} recorded searches, "
        f"{len(MD_DISTINCT)} exhaustive counts, {len(TEX_SNIPPETS)} snippets"
    )


if __name__ == "__main__":
    main()
