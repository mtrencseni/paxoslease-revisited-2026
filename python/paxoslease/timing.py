from __future__ import annotations

from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class ClockRateBounds:
    """Bounds for elapsed local-clock measurement.

    The convention is r_min * real_elapsed <= local_elapsed <= r_max * real_elapsed.
    """

    r_min: float
    r_max: float

    def __post_init__(self) -> None:
        if self.r_min <= 0 or self.r_max <= 0:
            raise ValueError("clock rates must be positive")
        if self.r_min > self.r_max:
            raise ValueError("r_min must be <= r_max")


@dataclass(frozen=True)
class TimingParameters:
    proposer_duration: int
    acceptor_duration: int
    quarantine_duration: int
    clock: ClockRateBounds = ClockRateBounds(1.0, 1.0)
    operation_margin: int = 0

    def __post_init__(self) -> None:
        for name in ("proposer_duration", "acceptor_duration", "quarantine_duration"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.operation_margin < 0:
            raise ValueError("operation_margin must be non-negative")

    @property
    def proposer_real_upper_bound(self) -> float:
        return (self.proposer_duration + self.operation_margin) / self.clock.r_min

    @property
    def acceptor_real_lower_bound(self) -> float:
        return self.acceptor_duration / self.clock.r_max

    @property
    def quarantine_real_lower_bound(self) -> float:
        return self.quarantine_duration / self.clock.r_max

    def validate(self) -> None:
        if self.proposer_real_upper_bound > self.acceptor_real_lower_bound:
            raise ValueError(
                "unsafe timer containment: proposer authority may outlast acceptor exclusion"
            )
        # Under the prepare-time timer rule, both a forgotten promise and a
        # forgotten accepted lease can only matter through a proposer attempt
        # whose Prepare preceded the crash, and that attempt is unusable one
        # proposer duration later.  The quarantine therefore needs to outlast
        # the proposer attempt in real time -- not the acceptor exclusion.
        if self.quarantine_real_lower_bound < self.proposer_real_upper_bound:
            raise ValueError(
                "unsafe quarantine: restarted acceptor may participate before forgotten facts expire"
            )


def derive_acceptor_duration(
    proposer_duration: int,
    clock: ClockRateBounds,
    operation_margin: int = 0,
) -> int:
    if proposer_duration <= 0:
        raise ValueError("proposer_duration must be positive")
    if operation_margin < 0:
        raise ValueError("operation_margin must be non-negative")
    return ceil((proposer_duration + operation_margin) * clock.r_max / clock.r_min)


def derive_quarantine_duration(
    proposer_duration: int,
    clock: ClockRateBounds,
    operation_margin: int = 0,
) -> int:
    if proposer_duration <= 0:
        raise ValueError("proposer_duration must be positive")
    # The quarantine, measured on the acceptor's (possibly fast) clock, must
    # cover the proposer attempt's real-time upper bound.
    forgotten_real = (proposer_duration + operation_margin) / clock.r_min
    return ceil(forgotten_real * clock.r_max)


def safe_timing_parameters(
    proposer_duration: int,
    clock: ClockRateBounds = ClockRateBounds(1.0, 1.0),
    operation_margin: int = 0,
) -> TimingParameters:
    acceptor = derive_acceptor_duration(proposer_duration, clock, operation_margin)
    quarantine = derive_quarantine_duration(proposer_duration, clock, operation_margin)
    params = TimingParameters(proposer_duration, acceptor, quarantine, clock, operation_margin)
    params.validate()
    return params
