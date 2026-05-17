"""Broker health probe."""

from __future__ import annotations

from hawkapi_taskiq import HealthReport, TaskIQConfig, check_broker, create_broker


async def test_in_memory_broker_is_healthy() -> None:
    broker = create_broker(TaskIQConfig())
    report = await check_broker(broker)
    assert isinstance(report, HealthReport)
    assert report.broker_ok is True
    assert report.broker_type == "InMemoryBroker"
