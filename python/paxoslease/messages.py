from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

# (counter, restart, node): the counter-major layout of the paper and of the
# audited production systems.  The counter is the most significant field, so
# ballots are comparable across proposers and grow with every attempt; the
# restart component is a durably stored counter incremented at every process
# start, so a ballot is never reused after volatile state is lost.  Note what
# the restart component does and does not give: uniqueness across restarts,
# not ordering.  The attempt counter restarts from zero under a higher
# restart component, and (1, restart+1, node) < (100, restart, node), so a
# restarted proposer may generate ballots below promises it obtained before
# the crash.  That is safe (the low ballot is rejected) but it stalls the
# proposer; liveness needs the catch-up rule of raising the counter above any
# ballot observed in responses, which the production systems implement.
Ballot = tuple[int, int, str]


class MessageKind(StrEnum):
    PREPARE = "prepare"
    PROMISE = "promise"
    ACCEPT = "accept"
    ACCEPTED = "accepted"
    RELEASE = "release"


@dataclass(frozen=True)
class Lease:
    owner: str
    ballot: Ballot
    deadline: int

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("lease owner must be non-empty")
        if self.deadline < 0:
            raise ValueError("lease deadline must be non-negative")


@dataclass(frozen=True)
class Message:
    kind: MessageKind | str
    src: str
    dst: str
    ballot: Optional[Ballot] = None
    lease: Optional[Lease] = None
    id: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", MessageKind(self.kind))
        if not self.src or not self.dst:
            raise ValueError("message src and dst must be non-empty")
        if self.id < 0:
            raise ValueError("message id must be non-negative")
