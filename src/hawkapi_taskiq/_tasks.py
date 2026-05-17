"""Task decorator + name-collision guard."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def task(
    broker: Any,
    *,
    name: str | None = None,
    queue: str | None = None,
    retry_on_error: bool = False,
    max_retries: int = 3,
    **task_kwargs: Any,
) -> Callable[[Callable[..., Any]], Any]:
    """Register a function as a TaskIQ task.

    - Detects ``async def`` automatically — runs as coroutine on the worker.
    - Sync functions are wrapped via TaskIQ's normal handling.
    - Collision detection: registering the same ``name`` twice raises
      ``ValueError`` (TaskIQ silently overrides; we disallow).
    """

    def decorator(fn: Callable[..., Any]) -> Any:
        task_name = name or f"{fn.__module__}.{fn.__qualname__}"
        existing = getattr(broker, "_hawkapi_task_names", None)
        if existing is None:
            existing = set()
            broker._hawkapi_task_names = existing
        if task_name in existing:
            raise ValueError(f"task name {task_name!r} already registered")
        existing.add(task_name)

        # Pop reserved keys from ``task_kwargs`` BEFORE merging — otherwise a
        # caller could pass ``task_name=`` in ``**task_kwargs`` and silently
        # bypass the duplicate-name guard above.
        task_kwargs.pop("task_name", None)
        kw: dict[str, Any] = {"task_name": task_name}
        if queue is not None:
            kw["queue"] = queue
        if retry_on_error:
            kw["retry_on_error"] = True
            kw["max_retries"] = max_retries
        kw.update(task_kwargs)

        return broker.task(**kw)(fn)

    return decorator


__all__ = ["task"]
