"""Task decorator + name collision."""

from __future__ import annotations

import pytest

from hawkapi_taskiq import TaskIQConfig, create_broker, task


def test_async_task_registers() -> None:
    broker = create_broker(TaskIQConfig())

    @task(broker, name="t.add")
    async def add(a: int, b: int) -> int:
        return a + b

    assert "t.add" in broker._hawkapi_task_names
    assert hasattr(add, "task_name") or callable(add)


def test_sync_task_registers() -> None:
    broker = create_broker(TaskIQConfig())

    @task(broker, name="t.work")
    def work(x: int) -> int:
        return x * 2

    assert "t.work" in broker._hawkapi_task_names


def test_duplicate_name_rejected() -> None:
    broker = create_broker(TaskIQConfig())

    @task(broker, name="t.dup")
    async def first() -> None:
        return None

    with pytest.raises(ValueError, match="already registered"):

        @task(broker, name="t.dup")
        async def second() -> None:
            return None


def test_task_name_override_via_kwargs_is_stripped() -> None:
    """Regression: ``task_name`` smuggled via ``**task_kwargs`` must NOT bypass
    the duplicate-name guard (defense in depth)."""
    broker = create_broker(TaskIQConfig())

    @task(broker, name="legit.first")
    async def first() -> None:
        return None

    # Attempt to bypass the collision check by overriding task_name via kwargs.
    @task(broker, name="legit.second", task_name="legit.first")
    async def second() -> None:
        return None

    # Both legitimate names are registered; the smuggled override was stripped.
    assert "legit.first" in broker._hawkapi_task_names
    assert "legit.second" in broker._hawkapi_task_names


def test_default_name_uses_qualname() -> None:
    broker = create_broker(TaskIQConfig())

    @task(broker)
    async def my_task() -> None:
        return None

    names = broker._hawkapi_task_names
    assert any("my_task" in n for n in names)
