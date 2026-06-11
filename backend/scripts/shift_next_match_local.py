"""
LOCAL-ONLY: shift the next scheduled match kickoff for prediction-lock testing.

Usage:
  docker compose exec backend python scripts/shift_next_match_local.py --confirm-local
  docker compose exec backend python scripts/shift_next_match_local.py --confirm-local --minutes 10
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://predico_user:predico_password@postgres:5432/predico_db"
    )
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-secret-key-for-script"
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "local"

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import AsyncSessionLocal
from app.db.models import Game
from app.db.models.game import GameStatus
from app.utils.match_time import get_game_kickoff_utc, get_prediction_deadline_utc, is_prediction_locked


def _assert_local_only() -> None:
    if os.getenv("DYNO"):
        raise SystemExit("Refusing to run on Heroku.")
    if os.getenv("ENVIRONMENT", "").lower() in {"production", "staging"}:
        raise SystemExit("Refusing to run outside local environment.")
    db_url = os.getenv("DATABASE_URL", "")
    for marker in ("herokuapp.com", "amazonaws.com", ".rds."):
        if marker in db_url:
            raise SystemExit("Refusing to run against a remote database.")


async def _find_next_game(session) -> Game | None:
    result = await session.execute(
        select(Game)
        .options(
            selectinload(Game.home_team),
            selectinload(Game.away_team),
        )
        .where(Game.status == GameStatus.SCHEDULED)
        .order_by(Game.match_date.asc(), Game.match_time.asc())
    )
    games = result.scalars().all()
    if not games:
        return None

    scheduled = [game for game in games if get_game_kickoff_utc(game) is not None]
    scheduled.sort(key=lambda game: get_game_kickoff_utc(game))
    return scheduled[0] if scheduled else games[0]


async def main(minutes: int) -> None:
    _assert_local_only()

    kickoff_utc = datetime.utcnow() + timedelta(minutes=minutes)
    sweden_offset_hours = 2
    venue_local = kickoff_utc + timedelta(hours=sweden_offset_hours)
    venue_local = venue_local.replace(microsecond=0)
    venue_time = venue_local.time().replace(microsecond=0)

    async with AsyncSessionLocal() as session:
        game = await _find_next_game(session)
        if not game:
            raise SystemExit("No scheduled games found.")

        game.match_date = venue_local.date()
        game.match_time = venue_time
        game.timezone = "UTC+2"
        game.scheduled_at = venue_local
        game.status = GameStatus.SCHEDULED

        await session.commit()
        await session.refresh(game)

        deadline = get_prediction_deadline_utc(game)
        locked = is_prediction_locked(game)

        home = game.home_team.name if game.home_team else str(game.home_team_id)
        away = game.away_team.name if game.away_team else str(game.away_team_id)
        print(f"Updated game #{game.id}: {home} vs {away}")
        print(f"Kickoff (Sweden): {venue_local.strftime('%a %b %d %H:%M')} (UTC+2)")
        print(f"Kickoff (UTC):      {kickoff_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        if deadline:
            print(f"Prediction lock:    {deadline.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"Predictions locked: {locked}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shift next match kickoff for local lock testing.")
    parser.add_argument("--minutes", type=int, default=10, help="Kickoff this many minutes from now.")
    parser.add_argument(
        "--confirm-local",
        action="store_true",
        help="Required safety flag confirming this is a local database.",
    )
    args = parser.parse_args()
    if not args.confirm_local:
        raise SystemExit("Pass --confirm-local to run against your local database.")
    asyncio.run(main(args.minutes))
