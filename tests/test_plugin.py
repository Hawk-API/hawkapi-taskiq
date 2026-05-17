"""init_taskiq + Depends(get_broker) end-to-end."""

from __future__ import annotations

from typing import Any

from hawkapi import Depends, HawkAPI
from hawkapi.testing import TestClient

from hawkapi_taskiq import TaskIQConfig, get_broker, init_taskiq, resolve_broker


def test_init_taskiq_attaches_to_state() -> None:
    app = HawkAPI(openapi_url=None, docs_url=None, redoc_url=None, scalar_url=None)
    broker = init_taskiq(app, config=TaskIQConfig(broker_url="memory://"))
    assert app.state.taskiq is broker


def test_resolve_falls_back_to_last() -> None:
    app = HawkAPI(openapi_url=None, docs_url=None, redoc_url=None, scalar_url=None)
    init_taskiq(app, config=TaskIQConfig(broker_url="memory://"))
    assert resolve_broker(None) is not None


def test_get_broker_dep_returns_broker() -> None:
    app = HawkAPI(openapi_url=None, docs_url=None, redoc_url=None, scalar_url=None)
    init_taskiq(app, config=TaskIQConfig(broker_url="memory://"))

    @app.get("/info")
    async def info(b: Any = Depends(get_broker)) -> dict[str, Any]:
        return {"type": type(b).__name__}

    client = TestClient(app)
    r = client.get("/info")
    assert r.status_code == 200
    assert r.json()["type"] == "InMemoryBroker"


def test_double_init_rejected() -> None:
    """Regression: calling ``init_taskiq`` twice on the same app would otherwise
    double-register startup/shutdown hooks."""
    import pytest as _pytest

    app = HawkAPI(openapi_url=None, docs_url=None, redoc_url=None, scalar_url=None)
    init_taskiq(app, config=TaskIQConfig(broker_url="memory://"))
    with _pytest.raises(RuntimeError, match="already been called"):
        init_taskiq(app, config=TaskIQConfig(broker_url="memory://"))


def test_get_broker_500_when_missing() -> None:
    app = HawkAPI(openapi_url=None, docs_url=None, redoc_url=None, scalar_url=None)

    @app.get("/x")
    async def x(b: Any = Depends(get_broker)) -> dict[str, Any]:
        return {"ok": True}

    import hawkapi_taskiq._plugin as _p

    saved = _p._LAST[0]
    _p._LAST[0] = None
    _p._ACTIVE.pop(app, None)
    try:
        r = TestClient(app).get("/x")
        assert r.status_code == 500
    finally:
        _p._LAST[0] = saved
