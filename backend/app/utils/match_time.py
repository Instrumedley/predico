"""
Match kickoff and prediction deadline helpers.

All stored datetimes are naive UTC. Venue-local kickoff is stored separately as
match_date + match_time + timezone (fixed UTC offset at kickoff).
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


def sweden_local_to_kickoff_utc(
    sweden_date: date,
    sweden_hour: int,
    sweden_minute: int,
) -> datetime:
    """
    Convert a kickoff time shown on FIFA.com for Sweden (CEST, UTC+2 in June)
    to naive UTC.
    """
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
    if game.scheduled_at:
        return game.scheduled_at

    if game.match_date and game.match_time and game.timezone:
        return get_match_datetime_utc(game.match_date, game.match_time, game.timezone)

    return None


def get_prediction_deadline_utc(game: "Game") -> Optional[datetime]:
    """Predictions lock one hour before kickoff."""
    kickoff = get_game_kickoff_utc(game)
    if not kickoff:
        return None
    return kickoff - timedelta(hours=PREDICTION_LOCK_HOURS_BEFORE_KICKOFF)


def is_prediction_locked(game: "Game", now: Optional[datetime] = None) -> bool:
    """True when predictions can no longer be created or updated."""
    if game.status.value != "scheduled":
        return True

    deadline = get_prediction_deadline_utc(game)
    if deadline is None:
        return False

    current = now or datetime.utcnow()
    return current >= deadline
