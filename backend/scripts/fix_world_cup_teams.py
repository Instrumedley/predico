"""
Apply 2026 World Cup team corrections to an existing database.

Renames teams in place (preserves game FKs). Run after updating populate_world_cup_data.py
or on a DB that still has Ireland / Italy / Romania.

Usage (Docker):
  docker compose exec backend python scripts/fix_world_cup_teams.py
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
from app.db.models.team import Team

# (old_name, new_name, country_code, flag_emoji)
TEAM_REPLACEMENTS = [
    ("Ireland", "Czechia", "CZE", "🇨🇿"),
    ("Italy", "Bosnia & Herzegovina", "BIH", "🇧🇦"),
    ("Romania", "Turkey", "TUR", "🇹🇷"),
]

# Ensure Paraguay flag emoji is correct (UI uses country_code PRY + flag-icons)
PARAGUAY_FLAG_FIX = ("Paraguay", "PRY", "🇵🇾")


async def main() -> None:
    print("Applying World Cup team corrections...")
    async with AsyncSessionLocal() as session:
        for old_name, new_name, code, flag in TEAM_REPLACEMENTS:
            result = await session.execute(select(Team).where(Team.name == old_name))
            team = result.scalar_one_or_none()
            if not team:
                result = await session.execute(select(Team).where(Team.name == new_name))
                team = result.scalar_one_or_none()
                if team:
                    print(f"  Skip {old_name} -> {new_name} (already updated)")
                else:
                    print(f"  WARNING: Neither {old_name} nor {new_name} found")
                continue

            team.name = new_name
            team.country_code = code
            team.flag_emoji = flag
            print(f"  Updated: {old_name} -> {new_name} ({code})")

        name, code, flag = PARAGUAY_FLAG_FIX
        result = await session.execute(select(Team).where(Team.name == name))
        paraguay = result.scalar_one_or_none()
        if paraguay:
            paraguay.country_code = code
            paraguay.flag_emoji = flag
            print(f"  Updated: {name} flag ({code})")
        else:
            print(f"  WARNING: {name} not found")

        await session.commit()

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
