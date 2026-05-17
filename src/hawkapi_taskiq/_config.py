"""TaskIQ configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskIQConfig:
    """Builder for a TaskIQ broker via :func:`hawkapi_taskiq.create_broker`."""

    broker_url: str = "memory://"
    """Broker connection string. Only ``memory://``, ``redis://``, ``rediss://``,
    ``nats://`` are accepted — anything else raises ``ValueError`` to prevent
    accidentally enabling unsafe-deserialization brokers."""

    result_backend_url: str = ""
    """Optional result-backend URL. Same scheme allowlist as ``broker_url``."""

    timezone: str = "UTC"
    task_default_queue: str = "default"
    serializer: str = "json"
    """Always ``"json"`` for v0.1.0. Other serializers are rejected at runtime
    to prevent arbitrary-deserialization vulns (CWE-502)."""

    extra: dict[str, Any] = field(default_factory=dict)
    """Forwarded as keyword args to the broker constructor."""


ALLOWED_BROKER_SCHEMES = frozenset({"memory", "redis", "rediss", "nats"})


def _scheme(url: str) -> str:
    return url.split("://", 1)[0].lower() if "://" in url else ""


__all__ = ["ALLOWED_BROKER_SCHEMES", "TaskIQConfig", "_scheme"]
