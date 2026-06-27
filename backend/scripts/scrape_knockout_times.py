"""
Update knockout kickoff times from world_cup_knockout_kickoffs.py.

Usage:
    python -m scripts.scrape_knockout_times
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db"
    )
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-secret-key-for-script"

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.db.models.game import Game
from app.services.knockout.knockout_sync_service import apply_kickoff_to_game
from scripts.world_cup_knockout_kickoffs import KNOCKOUT_KICKOFFS_BY_MATCH


async def main() -> None:
    updated = 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Game).where(Game.is_knockout.is_(True), Game.match_number.isnot(None))
        )
        games = result.scalars().all()

        for game in games:
            kickoff = KNOCKOUT_KICKOFFS_BY_MATCH.get(game.match_number)
            if not kickoff:
                continue
            match_date, hour, minute, venue_offset = kickoff
            apply_kickoff_to_game(game, match_date, hour, minute, venue_offset)
            updated += 1

        await session.commit()

    print(f"Updated kickoff times for {updated} knockout games")


if __name__ == "__main__":
    asyncio.run(main())
