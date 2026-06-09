"""
Update group-stage kickoff times from official FIFA schedule data.

Times were taken from FIFA.com (country=SE) and converted with
fifa_schedule_time_to_kickoff_utc() — afternoon/evening values are UTC;
early-morning values are Sweden local (CEST).

Usage:
    python -m scripts.scrape_match_times
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db"
    )
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-secret-key-for-script"

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import AsyncSessionLocal
from app.db.models.game import Game
from app.utils.match_time import (
    fifa_schedule_time_to_kickoff_utc,
    utc_to_venue_local,
    parse_timezone_offset,
)
from scripts.world_cup_kickoffs import FIFA_GROUP_STAGE_KICKOFFS


def build_kickoff_lookup() -> Dict[Tuple[str, str], Tuple[datetime, object, str]]:
    """
    Build lookup: (home_team, away_team) -> (scheduled_at_utc, match_time, timezone)
    """
    lookup: Dict[Tuple[str, str], Tuple[datetime, object, str]] = {}

    for home, away, schedule_date, hour, minute, venue_offset in FIFA_GROUP_STAGE_KICKOFFS:
        kickoff_utc = fifa_schedule_time_to_kickoff_utc(schedule_date, hour, minute)
        match_time, timezone = utc_to_venue_local(kickoff_utc, venue_offset)
        lookup[(home, away)] = (kickoff_utc, match_time, timezone)

    return lookup


async def update_game_times(session) -> None:
    """Update all group-stage games matched by home/away team names."""
    kickoff_lookup = build_kickoff_lookup()
    print(f"Loaded {len(kickoff_lookup)} kickoff entries from FIFA schedule\n")

    games_result = await session.execute(
        select(Game).options(
            selectinload(Game.home_team),
            selectinload(Game.away_team),
        )
    )
    games = games_result.scalars().all()

    updated_count = 0
    not_found_count = 0

    for game in games:
        home_team_name = game.home_team.name
        away_team_name = game.away_team.name
        key = (home_team_name, away_team_name)

        kickoff_info = kickoff_lookup.get(key)
        if not kickoff_info:
            not_found_count += 1
            print(f"  ✗ Not found: {home_team_name} vs {away_team_name} ({game.match_date})")
            continue

        kickoff_utc, match_time, timezone = kickoff_info
        venue_local = kickoff_utc + timedelta(hours=parse_timezone_offset(timezone))
        game.scheduled_at = kickoff_utc
        game.match_date = venue_local.date()
        game.match_time = match_time
        game.timezone = timezone
        updated_count += 1
        print(
            f"  ✓ Updated: {home_team_name} vs {away_team_name} "
            f"→ {match_time} {timezone} (UTC {kickoff_utc.strftime('%Y-%m-%d %H:%M')})"
        )

    await session.commit()
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  ✓ Updated: {updated_count} games")
    print(f"  ✗ Not found: {not_found_count} games")
    print("=" * 80)


async def main() -> None:
    print("=" * 80)
    print("Updating match kickoff times from FIFA schedule")
    print("=" * 80)
    print()

    async with AsyncSessionLocal() as session:
        await update_game_times(session)

    print("✓ Match times update complete!")


if __name__ == "__main__":
    asyncio.run(main())
