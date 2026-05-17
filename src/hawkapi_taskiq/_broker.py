"""Broker factory — URL-scheme dispatch with strict allowlist."""

from __future__ import annotations

from typing import Any

from ._config import ALLOWED_BROKER_SCHEMES, TaskIQConfig, _scheme


def create_broker(config: TaskIQConfig | None = None) -> Any:
    """Build an :class:`AsyncBroker` from ``config``. Raises ``ValueError`` for
    any URL scheme not in :data:`ALLOWED_BROKER_SCHEMES`."""
    cfg = config or TaskIQConfig()

    if cfg.serializer != "json":
        raise ValueError(
            f"hawkapi-taskiq only supports the JSON serializer in v0.1.0; got {cfg.serializer!r}"
        )

    # Defense in depth — block ``serializer`` from ``extra`` so a future broker
    # release that accepts the kwarg cannot bypass the JSON-only guarantee above.
    if "serializer" in cfg.extra:
        raise ValueError("'serializer' in extra is not permitted; JSON is enforced")

    broker_url = cfg.broker_url.strip()
    scheme = _scheme(broker_url)
    if scheme not in ALLOWED_BROKER_SCHEMES:
        raise ValueError(
            f"broker_url scheme {scheme!r} is not in the allowlist "
            f"{sorted(ALLOWED_BROKER_SCHEMES)!r}"
        )

    if cfg.result_backend_url:
        # v0.1.0 does not yet plumb result_backend_url through to the broker —
        # raise early so a misconfigured result backend cannot be silently dropped.
        raise NotImplementedError(
            "result_backend_url is not wired in v0.1.0; configure the result backend "
            "on the broker directly via TaskIQConfig.extra"
        )

    if scheme == "memory":
        from taskiq import InMemoryBroker

        return InMemoryBroker()

    if scheme in ("redis", "rediss"):
        try:
            from taskiq_redis import ListQueueBroker  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "taskiq-redis is required for redis brokers; pip install 'hawkapi-taskiq[redis]'"
            ) from exc
        return ListQueueBroker(url=broker_url, **cfg.extra)

    if scheme == "nats":
        try:
            from taskiq_nats import NatsBroker  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "taskiq-nats is required for nats brokers; pip install 'hawkapi-taskiq[nats]'"
            ) from exc
        return NatsBroker(servers=[broker_url], **cfg.extra)

    # Unreachable — the allowlist check above gates this.
    raise ValueError(f"unsupported scheme {scheme!r}")


__all__ = ["create_broker"]
