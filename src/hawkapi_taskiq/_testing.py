"""Test helpers — in-memory broker fixture."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from ._broker import create_broker
from ._config import TaskIQConfig


@asynccontextmanager
async def in_memory_broker() -> AsyncGenerator[Any, None]:
    """Yield a started InMemoryBroker; shut it down on exit."""
    broker = create_broker(TaskIQConfig(broker_url="memory://"))
    await broker.startup()
    try:
        yield broker
    finally:
        await broker.shutdown()


__all__ = ["in_memory_broker"]
