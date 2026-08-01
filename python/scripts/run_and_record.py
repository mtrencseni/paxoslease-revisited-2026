from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


COMMANDS = [
    ("tool-versions", ["bash", "-lc", "java -version 2>&1; tlapm --version; sany >/dev/null 2>&1; tlc -h 2>&1 | head -n 3; python --version; .venv/bin/python -m pytest --version; jar=$(grep -oE '[^ ]*tla2tools[^ ]*\\.jar' \"$(command -v tlc)\" | head -n 1); [ -n \"$jar\" ] && sha256sum \"$jar\" || echo 'tla2tools.jar not located from tlc wrapper'"]),
    ("parse", ["make", "parse"]),
    ("lint", ["make", "lint"]),
    ("check-standalone", ["make", "check-standalone"]),
    ("check-composition", ["make", "check-composition"]),
    ("counterexamples", ["make", "counterexamples"]),
    ("check-impl", ["make", "check-impl"]),
    ("unsafe-configs", ["make", "unsafe-configs"]),
    ("prove", ["make", "prove"]),
    ("test", ["make", "test"]),
    ("monte-carlo", ["make", "monte-carlo"]),
    ("expected-counterexamples", ["make", "expected-counterexamples"]),
    ("variant-check", ["make", "variant-check"]),
    ("trace-smoke-test", ["make", "trace-smoke-test"]),
    ("timing-examples", ["make", "timing-examples"]),
]


def run(name: str, cmd: list[str]) -> tuple[str, bool]:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    ok = proc.returncode == 0
    status = "PASS" if ok else f"FAIL ({proc.returncode})"
    section = f"## {name}\n\nCommand: `{' '.join(cmd)}`\n\nStatus: **{status}**\n\n```text\n{proc.stdout}\n```\n"
    return section, ok


def main() -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    sections = [f"# Verification and Test Results\n\nGenerated: `{stamp}`\n"]
    failures = []
    for name, cmd in COMMANDS:
        section, ok = run(name, cmd)
        sections.append(section)
        if not ok:
            failures.append(name)
    text = "\n".join(sections)
    (RESULTS / "verification-results.md").write_text(text, encoding="utf-8")
    print("wrote results/verification-results.md")
    # Validate the freshly recorded outputs against the numbers the paper
    # cites; runs after the report is written so it checks this run, not
    # the previous one.
    claims, claims_ok = run("paper-claims", ["make", "paper-claims"])
    (RESULTS / "verification-results.md").write_text(
        text + "\n" + claims, encoding="utf-8"
    )
    if not claims_ok:
        failures.append("paper-claims")
    # A verification report that records failures must not itself report
    # success: the recording is evidence, and the exit status is the
    # fail-fast contract that `make results` and `make paper-evidence`
    # rely on.
    if failures:
        print(f"FAILED sections: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
