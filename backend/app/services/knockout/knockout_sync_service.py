"""Sync knockout bracket resolution into games rows."""

from __future__ import annotations

from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.game import Game
from app.services.knockout.bracket_service import ResolvedMatch, resolve_all_knockout_matches
from app.utils.match_time import format_timezone_offset, parse_timezone_offset


async def sync_knockout_game_teams(db: AsyncSession) -> int:
    """
    Set home_team_id / away_team_id on knockout games from bracket resolution.
    Clears FKs when a slot is still TBD.
    """
    resolved = await resolve_all_knockout_matches(db)

    query = select(Game).where(Game.is_knockout.is_(True), Game.match_number.isnot(None))
    result = await db.execute(query)
    games = result.scalars().all()

    updated = 0
    for game in games:
        match_number = game.match_number
        if match_number is None or match_number not in resolved:
            continue

        resolved_match = resolved[match_number]
        new_home_id = resolved_match.home.team.team_id if resolved_match.home.team else None
        new_away_id = resolved_match.away.team.team_id if resolved_match.away.team else None

        if game.home_team_id != new_home_id or game.away_team_id != new_away_id:
            game.home_team_id = new_home_id
            game.away_team_id = new_away_id
            updated += 1

    if updated:
        await db.commit()

    return updated


async def get_knockout_game_by_match_number(
    db: AsyncSession,
    match_number: int,
) -> Game | None:
    query = select(Game).where(
        Game.is_knockout.is_(True),
        Game.match_number == match_number,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


def apply_kickoff_to_game(
    game: Game,
    match_date,
    hour: int,
    minute: int,
    venue_offset_hours: int,
) -> None:
    """Set match_date, match_time, timezone, and scheduled_at on a game."""
    match_time = time(hour, minute)
    timezone_str = format_timezone_offset(venue_offset_hours)
    venue_local = datetime.combine(match_date, match_time)
    scheduled_at = venue_local - timedelta(hours=parse_timezone_offset(timezone_str))

    game.match_date = match_date
    game.match_time = match_time
    game.timezone = timezone_str
    game.scheduled_at = scheduled_at


def resolved_match_to_slot_labels(resolved: ResolvedMatch | None) -> tuple[str | None, str | None]:
    if not resolved:
        return None, None

    home_label = resolved.home.label if not resolved.home.team else None
    away_label = resolved.away.label if not resolved.away.team else None
    return home_label, away_label
