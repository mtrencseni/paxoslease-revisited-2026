from __future__ import annotations

import json
from pathlib import Path

from paxoslease.timing import ClockRateBounds, safe_timing_parameters

def main() -> None:
    examples = []
    for r_min, r_max, proposer, margin in [
        (1.0, 1.0, 4, 0),
        (0.99, 1.01, 1000, 10),
    ]:
        params = safe_timing_parameters(proposer, ClockRateBounds(r_min, r_max), margin)
        examples.append(
            {
                "r_min": r_min,
                "r_max": r_max,
                "proposer_duration": params.proposer_duration,
                "operation_margin": margin,
                "acceptor_duration": params.acceptor_duration,
                "quarantine_duration": params.quarantine_duration,
                "proposer_real_upper_bound": params.proposer_real_upper_bound,
                "acceptor_real_lower_bound": params.acceptor_real_lower_bound,
                "quarantine_real_lower_bound": params.quarantine_real_lower_bound,
            }
        )
    out = Path(__file__).resolve().parents[2] / "results" / "timing-examples.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(examples, indent=2, sort_keys=True) + "\n")
    print(out.read_text(), end="")

if __name__ == "__main__":
    main()
