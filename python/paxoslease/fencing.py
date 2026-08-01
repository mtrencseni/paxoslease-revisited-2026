from __future__ import annotations

from dataclasses import dataclass, field

from .messages import Ballot


@dataclass
class FencedResource:
    """Resource that rejects commands with stale fencing tokens."""

    highest_token: Ballot | None = None
    accepted: list[tuple[Ballot, str]] = field(default_factory=list)

    def apply(self, token: Ballot, command: str) -> bool:
        if self.highest_token is not None and token < self.highest_token:
            return False
        self.highest_token = token
        self.accepted.append((token, command))
        return True


@dataclass
class UnfencedResource:
    accepted: list[tuple[Ballot, str]] = field(default_factory=list)

    def apply(self, token: Ballot, command: str) -> bool:
        self.accepted.append((token, command))
        return True
