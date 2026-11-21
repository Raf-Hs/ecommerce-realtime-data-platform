"""Tests for the replay producer (unit-level, no Kafka required)."""

import pytest

from src.producers.replay import ReplayProducer


def test_invalid_replay_speed_raises() -> None:
    with pytest.raises(ValueError):
        ReplayProducer(replay_speed=0)
    with pytest.raises(ValueError):
        ReplayProducer(replay_speed=-1)