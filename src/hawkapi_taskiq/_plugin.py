"""init_taskiq + get_broker + WeakKeyDictionary registry."""

from __future__ import annotations

from typing import Any
from weakref import WeakKeyDictionary

from hawkapi import HTTPException, Request

from ._broker import create_broker
from ._config import TaskIQConfig


class _StateNamespace:
    taskiq: Any


_ACTIVE: WeakKeyDictionary[Any, Any] = WeakKeyDictionary()
_LAST: list[Any | None] = [None]


def init_taskiq(
    app: Any,
    *,
    broker: Any = None,
    config: TaskIQConfig | None = None,
    auto_startup: bool = True,
) -> Any:
    """Attach a TaskIQ broker to ``app.state.taskiq``.

    Pass ``broker=`` with a pre-built broker, or ``config=`` to construct one
    via :func:`create_broker`. ``auto_startup=True`` wires ``broker.startup()``
    and ``broker.shutdown()`` into the app lifecycle.
    """
    if broker is None:
        broker = create_broker(config)

    # Reject double-initialisation — registering lifecycle hooks twice would
    # call startup()/shutdown() on the stale broker after this one replaces it.
    if getattr(app, "state", None) is not None and getattr(app.state, "taskiq", None) is not None:
        raise RuntimeError(
            "init_taskiq has already been called on this app; create a new app or "
            "drop the previous broker explicitly before re-initialising"
        )

    if getattr(app, "state", None) is None:
        app.state = _StateNamespace()
    app.state.taskiq = broker
    try:
        _ACTIVE[app] = broker
    except TypeError:
        pass
    _LAST[0] = broker

    if auto_startup and hasattr(app, "on_startup"):

        async def _start() -> None:
            startup = getattr(broker, "startup", None)
            if startup is not None:
                await startup()

        app.on_startup(_start)

    if auto_startup and hasattr(app, "on_shutdown"):

        async def _stop() -> None:
            shutdown = getattr(broker, "shutdown", None)
            if shutdown is not None:
                await shutdown()

        app.on_shutdown(_stop)

    return broker


def resolve_broker(app: Any) -> Any | None:
    if app is None:
        return _LAST[0]
    try:
        found = _ACTIVE.get(app)
    except TypeError:
        found = None
    if found is not None:
        return found
    state = getattr(app, "state", None)
    if state is not None and hasattr(state, "taskiq"):
        return state.taskiq
    return _LAST[0]


def get_broker(request: Request) -> Any:
    broker = resolve_broker(request.scope.get("app"))
    if broker is None:
        raise HTTPException(500, detail="TaskIQ not configured — call init_taskiq(app, ...) first")
    return broker


__all__ = ["get_broker", "init_taskiq", "resolve_broker"]
