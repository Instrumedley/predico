"""
Match kickoff and prediction deadline helpers.

Canonical kickoff instant is derived from match_date + match_time + timezone
(venue-local wall clock converted to naive UTC). scheduled_at mirrors the same
venue-local wall clock as match_time for easier DB inspection; do not treat it
as UTC.
"""
from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.game import Game

PREDICTION_LOCK_HOURS_BEFORE_KICKOFF = 1


def parse_timezone_offset(timezone_str: str) -> int:
    """Parse strings like 'UTC-5' or 'UTC+3' into offset hours."""
    if not timezone_str:
        return 0

    match = re.match(r"UTC([+-]?\d+)", timezone_str.strip(), re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def format_timezone_offset(offset_hours: int) -> str:
    """Format offset hours as a UTC offset string."""
    if offset_hours >= 0:
        return f"UTC+{offset_hours}"
    return f"UTC{offset_hours}"


def get_match_datetime_utc(
    match_date: date,
    match_time: Optional[time],
    timezone_str: Optional[str],
) -> Optional[datetime]:
    """
    Convert venue-local kickoff to naive UTC datetime.
    Returns None if match_time or timezone is missing.
    """
    if not match_date or not match_time or not timezone_str:
        return None

    tz_offset_hours = parse_timezone_offset(timezone_str)
    local_datetime = datetime.combine(match_date, match_time)
    return local_datetime - timedelta(hours=tz_offset_hours)


def fifa_schedule_time_to_kickoff_utc(
    schedule_date: date,
    hour: int,
    minute: int,
) -> datetime:
    """
    Convert a time from FIFA.com's schedule feed to naive UTC kickoff.

    Values in world_cup_kickoffs.py are the raw UTC kickoff times from the FIFA
    fixtures feed (country=SE). The site adds +2h for Sweden (CEST) in the
    browser, e.g. 02:00 UTC → 04:00 Sweden, 19:00 UTC → 21:00 Sweden.
    """
    return datetime.combine(schedule_date, time(hour, minute))


def sweden_local_to_kickoff_utc(
    sweden_date: date,
    sweden_hour: int,
    sweden_minute: int,
) -> datetime:
    """Convert an explicit Sweden (CEST, UTC+2) kickoff display time to UTC."""
    sweden_local = datetime.combine(sweden_date, time(sweden_hour, sweden_minute))
    return sweden_local - timedelta(hours=2)


def utc_to_venue_local(
    kickoff_utc: datetime,
    venue_offset_hours: int,
) -> tuple[time, str]:
    """Derive venue-local kickoff time and timezone label from UTC."""
    venue_local = kickoff_utc + timedelta(hours=venue_offset_hours)
    return venue_local.time(), format_timezone_offset(venue_offset_hours)


def get_game_kickoff_utc(game: "Game") -> Optional[datetime]:
    """Return canonical kickoff instant for a game (naive UTC)."""
    if game.match_date and game.match_time and game.timezone:
        return get_match_datetime_utc(game.match_date, game.match_time, game.timezone)

    if game.scheduled_at:
        return game.scheduled_at

    return None


def get_prediction_deadline_utc(game: "Game") -> Optional[datetime]:
    """Predictions lock one hour before kickoff."""
    kickoff = get_game_kickoff_utc(game)
    if not kickoff:
        return None
    return kickoff - timedelta(hours=PREDICTION_LOCK_HOURS_BEFORE_KICKOFF)


def are_teams_resolved(game: "Game") -> bool:
    """True when both home and away teams are assigned."""
    return game.home_team_id is not None and game.away_team_id is not None


def is_prediction_locked(game: "Game", now: Optional[datetime] = None) -> bool:
    """True when predictions can no longer be created or updated."""
    if game.status.value != "scheduled":
        return True

    if game.is_knockout and not are_teams_resolved(game):
        return True

    deadline = get_prediction_deadline_utc(game)
    if deadline is None:
        return False

    current = now or datetime.utcnow()
    return current >= deadline
