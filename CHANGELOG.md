# Changelog

## 0.1.0 — 2026-05-17

Initial release.

Security review applied before ship:

- `task_name` smuggled via `**task_kwargs` no longer bypasses the duplicate-name guard (defense in depth).
- `extra={"serializer": ...}` is rejected to prevent a future broker release accepting that kwarg from bypassing the JSON-only enforcement (CWE-502 hardening).
- `result_backend_url` now raises `NotImplementedError` rather than silently dropping the value — a misconfigured result backend can no longer be ignored.
- Double-init guard on `init_taskiq` — calling it twice on the same app raises rather than double-registering startup/shutdown hooks.
- `check_broker` actually probes the broker (was a static `True` before) and scrubs Redis/NATS credentials from any error string.
- `add_scheduled` removed from the public API — it set labels in a format `TaskiqScheduler` does not consume. `Scheduled` remains as a cron-validation value type; README shows the direct `LabelScheduleSource` wiring.

Features:

- `create_broker(TaskIQConfig(...))` — URL-scheme allowlist (`memory://`, `redis://`, `rediss://`, `nats://`), JSON serializer enforced at construction.
- `@task(broker, ...)` decorator with duplicate-name detection.
- `Scheduled` value type with cron-syntax validation via `croniter` (extras `[cron]`).
- `init_taskiq(app, ...)` wires startup/shutdown into the app lifecycle. `Depends(get_broker)` + `WeakKeyDictionary` registry.
- `check_broker()` health probe + `HealthReport` with credential scrubbing.
- `in_memory_broker()` async context manager for tests.
- Extras: `[redis]` (taskiq-redis), `[nats]` (taskiq-nats), `[cron]` (croniter).
