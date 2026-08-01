from __future__ import annotations

import json
from pathlib import Path

from paxoslease.counterexamples import COUNTEREXAMPLES

def main() -> None:
    results = [fn() for fn in COUNTEREXAMPLES]
    payload = [
        {
            "scenario": r.scenario,
            "category": r.category,
            "violated_invariant": r.violated_invariant,
            "minimal_fix": r.minimal_fix,
            "trace": list(r.trace),
        }
        for r in results
    ]
    out = Path(__file__).resolve().parents[2] / "results" / "counterexamples.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for item in payload:
        print(f"{item['scenario']} [{item['category']}]: {item['violated_invariant']}")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
