"""hawkapi-taskiq — TaskIQ integration for HawkAPI.

Modern async-native task queue. URL-scheme allowlist enforces JSON-only
serialization to prevent arbitrary-deserialization vulnerabilities. Broker
DI via ``init_taskiq(app, ...)`` + ``Depends(get_broker)``. ``Scheduled``
provides cron-syntax validation; wire it into TaskIQ's own scheduler
sources (see README).
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ._broker import create_broker
from ._config import ALLOWED_BROKER_SCHEMES, TaskIQConfig
from ._health import HealthReport, check_broker
from ._plugin import get_broker, init_taskiq, resolve_broker
from ._schedule import Scheduled
from ._tasks import task
from ._testing import in_memory_broker

try:
    __version__ = version("hawkapi-taskiq")
except PackageNotFoundError:  # pragma: no cover - running from a source tree without install
    __version__ = "0.0.0"

__all__ = [
    "ALLOWED_BROKER_SCHEMES",
    "HealthReport",
    "Scheduled",
    "TaskIQConfig",
    "__version__",
    "check_broker",
    "create_broker",
    "get_broker",
    "in_memory_broker",
    "init_taskiq",
    "resolve_broker",
    "task",
]
