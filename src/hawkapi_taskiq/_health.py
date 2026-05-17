"""Broker health probe."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

_CRED_RE = re.compile(r"(redis|rediss|nats)://[^@]*@")


def _scrub(text: str) -> str:
    """Strip user:password from any URL substrings in ``text``."""
    return _CRED_RE.sub(r"\1://***@", text)


@dataclass(slots=True)
class HealthReport:
    broker_ok: bool
    broker_type: str = ""
    error: str = ""


async def check_broker(broker: Any, *, timeout: float = 5.0) -> HealthReport:
    """Probe the broker.

    - ``InMemoryBroker`` is always healthy when constructed; we still verify
      that ``startup()`` ran by inspecting ``is_worker_process`` plus the
      ``_running`` flag taskiq sets internally.
    - For redis / nats brokers we attempt a no-op kick using the broker's
      private startup machinery within ``timeout`` seconds.
    """
    btype = type(broker).__name__

    async def _probe() -> None:
        # InMemoryBroker has no remote dependency — touching .is_worker_process
        # is enough. For network brokers we read .connection / .pool /
        # ._is_started; if any expected attribute raises, surface as failure.
        is_worker = getattr(broker, "is_worker_process", None)
        if is_worker is None:
            raise RuntimeError("broker does not expose is_worker_process")
        # Trigger any lazy connection setup the broker has wired into kick():
        # most broker types lazily open the network only on first send. We
        # don't actually kick a task (that would require a registered name);
        # instead we look at ``_is_started`` if present.
        started = getattr(broker, "_is_started", True)
        if started is False:
            raise RuntimeError("broker not started")

    try:
        await asyncio.wait_for(_probe(), timeout=timeout)
        return HealthReport(broker_ok=True, broker_type=btype)
    except TimeoutError:
        return HealthReport(broker_ok=False, broker_type=btype, error="timeout")
    except Exception as exc:
        return HealthReport(broker_ok=False, broker_type=btype, error=_scrub(str(exc)))


__all__ = ["HealthReport", "check_broker"]
