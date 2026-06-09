"""Tests for match kickoff and prediction lock helpers."""
from datetime import date, datetime, time

from app.db.models.game import Game, GameStatus
from app.utils.match_time import (
    get_game_kickoff_utc,
    get_match_datetime_utc,
    get_prediction_deadline_utc,
    is_prediction_locked,
    sweden_local_to_kickoff_utc,
)


def test_sweden_local_to_kickoff_utc():
    kickoff = sweden_local_to_kickoff_utc(date(2026, 6, 11), 19, 0)
    assert kickoff == datetime(2026, 6, 11, 17, 0)


def test_get_match_datetime_utc():
    kickoff = get_match_datetime_utc(date(2026, 6, 11), time(12, 0), "UTC-5")
    assert kickoff == datetime(2026, 6, 11, 17, 0)


def test_prediction_lock_one_hour_before_kickoff():
    game = Game(
        id=1,
        home_team_id=1,
        away_team_id=2,
        scheduled_at=datetime(2026, 6, 11, 17, 0),
        match_date=date(2026, 6, 11),
        match_time=time(12, 0),
        timezone="UTC-5",
        status=GameStatus.SCHEDULED,
        round_id=1,
    )

    assert get_game_kickoff_utc(game) == datetime(2026, 6, 11, 17, 0)
    assert get_prediction_deadline_utc(game) == datetime(2026, 6, 11, 16, 0)
    assert not is_prediction_locked(game, now=datetime(2026, 6, 11, 15, 59))
    assert is_prediction_locked(game, now=datetime(2026, 6, 11, 16, 0))
