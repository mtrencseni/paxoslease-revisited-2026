from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TraceEvent:
    step: int
    time: int
    event: str
    parameters: dict[str, Any]
    before: dict[str, Any]
    after: dict[str, Any]
    invariant_ok: bool
    violation: str | None = None


@dataclass
class TraceRecorder:
    events: list[TraceEvent] = field(default_factory=list)

    def append(self, event: TraceEvent) -> None:
        self.events.append(event)

    def to_jsonable(self) -> list[dict[str, Any]]:
        return [event.__dict__ for event in self.events]
