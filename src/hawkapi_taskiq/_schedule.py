"""Cron-syntax validator for schedule entries.

For v0.1.0 we ship only the value-type :class:`Scheduled` with validation —
it is up to the operator to wire it into TaskIQ's native scheduler sources.
See README for the recommended pattern.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Scheduled:
    """A schedule descriptor with validation at construction time."""

    cron: str = ""
    interval_seconds: float = 0.0

    def __post_init__(self) -> None:
        if (self.cron and self.interval_seconds) or (not self.cron and not self.interval_seconds):
            raise ValueError("Scheduled requires exactly one of `cron` or `interval_seconds`")
        if self.cron:
            # Validate cron syntax up-front. croniter is an optional dep — if not
            # installed, we skip validation rather than fail registration.
            try:
                from croniter import croniter  # type: ignore[import-not-found]
            except ImportError:
                return
            if not croniter.is_valid(self.cron):
                raise ValueError(f"invalid cron expression: {self.cron!r}")
        elif self.interval_seconds <= 0:
            raise ValueError("interval_seconds must be > 0")


__all__ = ["Scheduled"]
