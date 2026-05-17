"""Scheduled — cron + interval validators."""

from __future__ import annotations

import pytest

from hawkapi_taskiq import Scheduled


def test_scheduled_requires_exactly_one_kind() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        Scheduled()
    with pytest.raises(ValueError, match="exactly one"):
        Scheduled(cron="0 0 * * *", interval_seconds=60.0)


def test_scheduled_validates_cron_when_croniter_available() -> None:
    # croniter is a [dev] dep so always present in tests.
    with pytest.raises(ValueError, match="invalid cron"):
        Scheduled(cron="not a cron")


def test_scheduled_accepts_valid_cron() -> None:
    s = Scheduled(cron="*/5 * * * *")
    assert s.cron == "*/5 * * * *"


def test_scheduled_rejects_non_positive_interval() -> None:
    with pytest.raises(ValueError, match="interval_seconds"):
        Scheduled(interval_seconds=0.0)
    with pytest.raises(ValueError, match="interval_seconds"):
        Scheduled(interval_seconds=-1.0)


def test_scheduled_accepts_positive_interval() -> None:
    s = Scheduled(interval_seconds=30.0)
    assert s.interval_seconds == 30.0
