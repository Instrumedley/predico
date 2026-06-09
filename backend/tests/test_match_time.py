"""Tests for match kickoff and prediction lock helpers."""
from datetime import date, datetime, time

from app.db.models.game import Game, GameStatus
from app.utils.match_time import (
    fifa_schedule_time_to_kickoff_utc,
    get_game_kickoff_utc,
    get_match_datetime_utc,
    get_prediction_deadline_utc,
    is_prediction_locked,
    sweden_local_to_kickoff_utc,
)


def test_mexico_opening_match_from_fifa_schedule():
    # FIFA feed: 19:00 UTC on 11 June → 21:00 in Sweden, 13:00 at UTC-6 (Wikipedia)
    kickoff = fifa_schedule_time_to_kickoff_utc(date(2026, 6, 11), 19, 0)
    assert kickoff == datetime(2026, 6, 11, 19, 0)

    venue_utc = get_match_datetime_utc(date(2026, 6, 11), time(13, 0), "UTC-6")
    assert venue_utc == datetime(2026, 6, 11, 19, 0)

    sweden = sweden_local_to_kickoff_utc(date(2026, 6, 11), 21, 0)
    assert sweden == datetime(2026, 6, 11, 19, 0)


def test_early_morning_fifa_schedule_is_utc():
    # FIFA feed: 02:00 UTC on 12 June → 04:00 in Sweden, 20:00 on 11 June at UTC-6
    kickoff = fifa_schedule_time_to_kickoff_utc(date(2026, 6, 12), 2, 0)
    assert kickoff == datetime(2026, 6, 12, 2, 0)

    venue_utc = get_match_datetime_utc(date(2026, 6, 11), time(20, 0), "UTC-6")
    assert venue_utc == datetime(2026, 6, 12, 2, 0)

    sweden = sweden_local_to_kickoff_utc(date(2026, 6, 12), 4, 0)
    assert sweden == datetime(2026, 6, 12, 2, 0)


def test_prediction_lock_one_hour_before_kickoff():
    game = Game(
        id=1,
        home_team_id=1,
        away_team_id=2,
        scheduled_at=datetime(2026, 6, 11, 19, 0),
        match_date=date(2026, 6, 11),
        match_time=time(13, 0),
        timezone="UTC-6",
        status=GameStatus.SCHEDULED,
        round_id=1,
    )

    assert get_game_kickoff_utc(game) == datetime(2026, 6, 11, 19, 0)
    assert get_prediction_deadline_utc(game) == datetime(2026, 6, 11, 18, 0)
    assert not is_prediction_locked(game, now=datetime(2026, 6, 11, 17, 59))
    assert is_prediction_locked(game, now=datetime(2026, 6, 11, 18, 0))
