"""Config + scheme allowlist."""

from __future__ import annotations

import pytest

from hawkapi_taskiq import ALLOWED_BROKER_SCHEMES, TaskIQConfig, create_broker


def test_default_config_uses_in_memory_broker() -> None:
    cfg = TaskIQConfig()
    assert cfg.broker_url == "memory://"
    assert cfg.serializer == "json"


def test_scheme_allowlist_blocks_unknown_scheme() -> None:
    with pytest.raises(ValueError, match="allowlist"):
        create_broker(TaskIQConfig(broker_url="amqp://localhost"))


def test_scheme_allowlist_blocks_file_scheme() -> None:
    with pytest.raises(ValueError, match="allowlist"):
        create_broker(TaskIQConfig(broker_url="file:///tmp/x"))


def test_unsafe_serializer_rejected() -> None:
    with pytest.raises(ValueError, match="JSON serializer"):
        create_broker(TaskIQConfig(serializer="msgpack"))


def test_result_backend_url_raises_not_implemented_in_v01() -> None:
    """Regression: result_backend_url is not yet plumbed through — raise so a
    misconfigured backend cannot be silently dropped."""
    with pytest.raises(NotImplementedError, match="result_backend_url"):
        create_broker(
            TaskIQConfig(
                broker_url="memory://",
                result_backend_url="redis://x",
            )
        )


def test_extra_serializer_key_rejected() -> None:
    """Regression: ``extra={"serializer": ...}`` must NOT bypass JSON enforcement
    even if future broker releases accept it as a constructor kwarg."""
    with pytest.raises(ValueError, match="serializer"):
        create_broker(
            TaskIQConfig(
                broker_url="memory://",
                extra={"serializer": "yaml"},
            )
        )


def test_broker_url_is_stripped() -> None:
    """Leading/trailing whitespace in broker_url is trimmed."""
    broker = create_broker(TaskIQConfig(broker_url="  memory://  "))
    assert broker is not None


def test_allowed_schemes_set_contents() -> None:
    assert "memory" in ALLOWED_BROKER_SCHEMES
    assert "redis" in ALLOWED_BROKER_SCHEMES
    assert "rediss" in ALLOWED_BROKER_SCHEMES
    assert "nats" in ALLOWED_BROKER_SCHEMES
    assert "amqp" not in ALLOWED_BROKER_SCHEMES
    assert "file" not in ALLOWED_BROKER_SCHEMES
