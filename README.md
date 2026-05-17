# hawkapi-taskiq

[TaskIQ](https://taskiq-python.github.io/) integration for [HawkAPI](https://github.com/Hawk-API/HawkAPI). Modern async-native task queue — a lighter, async-first alternative to Celery.

## Install

```bash
pip install hawkapi-taskiq
pip install 'hawkapi-taskiq[redis]'    # + taskiq-redis
pip install 'hawkapi-taskiq[nats]'     # + taskiq-nats
pip install 'hawkapi-taskiq[cron]'     # + croniter for schedule validation
```

## Quickstart

```python
from hawkapi import Depends, HawkAPI
from hawkapi_taskiq import TaskIQConfig, get_broker, init_taskiq, task

app = HawkAPI()
broker = init_taskiq(app, config=TaskIQConfig(broker_url="redis://localhost:6379/0"))


@task(broker, name="emails.send")
async def send_email(to: str, subject: str) -> None:
    ...


@app.post("/notify")
async def notify(email: str, b = Depends(get_broker)):
    await send_email.kiq(email, "Hello")
    return {"ok": True}
```

## Broker selection

Choose by URL scheme — all others are rejected:

| URL | Broker |
|---|---|
| `memory://` | `InMemoryBroker` (tests, single-process) |
| `redis://host:6379/0` | `ListQueueBroker` (taskiq-redis) |
| `rediss://...` | same, with TLS |
| `nats://server:4222` | `NatsBroker` (taskiq-nats) |

Any other scheme raises `ValueError` at `create_broker()` — this is a security feature, not a limitation. The allowlist prevents accidentally enabling brokers that use unsafe deserialization formats.

## Scheduling

v0.1.0 ships a `Scheduled` value type with cron-syntax validation. Wire it to TaskIQ's native scheduler yourself — we deliberately avoid a "magic" registration helper that doesn't compose cleanly with the upstream `TaskiqScheduler`:

```python
from hawkapi_taskiq import Scheduled
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource


@task(broker, name="myapp.cleanup")
async def cleanup() -> None:
    ...


# 1. Validate the schedule (cron syntax) up front.
schedule = Scheduled(cron="0 * * * *")    # raises ValueError if malformed

# 2. Apply it as a label LabelScheduleSource reads.
cleanup.labels["schedule"] = [{"cron": schedule.cron, "args": [], "kwargs": {}}]


# 3. Run a scheduler process alongside the worker.
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
```

`Scheduled(cron="...")` validates via [`croniter`](https://github.com/kiorky/croniter) (install with `[cron]` extra). Both `cron` and `interval_seconds` set are rejected (exactly one is required).

## Health

```python
from hawkapi_taskiq import check_broker

report = await check_broker(broker)
# HealthReport(broker_ok=True, broker_type="ListQueueBroker", error="")
```

## Testing

```python
from hawkapi_taskiq import in_memory_broker, task


async def test_my_task():
    async with in_memory_broker() as broker:
        @task(broker, name="t.work")
        async def work(x: int) -> int:
            return x * 2

        await work.kiq(21)
        # Execute pending tasks via TaskIQ's normal flow.
```

## Security

- **JSON-only serialization** — TaskIQ defaults are fine; we explicitly reject any other serializer via `TaskIQConfig.serializer` to prevent arbitrary-deserialization at consume time (CWE-502).
- **Broker URL scheme allowlist** — only `memory://`, `redis://`, `rediss://`, `nats://`.
- **Task name registry** — duplicate `@task(name=...)` raises at registration. TaskIQ silently overrides; we disallow.
- **Cron expression validation** at registration time — malformed expressions fail fast.

## Development

```bash
git clone https://github.com/Hawk-API/hawkapi-taskiq.git
cd hawkapi-taskiq
uv sync --extra dev
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run pyright src/
```

## License

MIT.
