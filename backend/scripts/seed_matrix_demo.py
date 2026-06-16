"""
Seed LOCAL-ONLY demo data for testing the league progress matrix view.

Creates:
  - 10 demo users with predictions on every finished match in the demo window
  - 1 public demo league "[LOCAL MATRIX DEMO] ..."
  - Ensures the first N tournament games are FINISHED (only snapshots games it changes)

Safety:
  - Refuses to run on Heroku (DYNO), production/staging ENVIRONMENT, or non-local DATABASE_URL
  - Requires --confirm-local on every run
  - Snapshots modified games to backend/.matrix_demo_snapshot.json and restores on --remove

Usage (Docker — recommended):
  docker compose exec backend python scripts/seed_matrix_demo.py --confirm-local
  docker compose exec backend python scripts/seed_matrix_demo.py --confirm-local --join-email you@gmail.com
  docker compose exec backend python scripts/seed_matrix_demo.py --confirm-local --remove
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import secrets
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://predico_user:predico_password@postgres:5432/predico_db"
    )
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-secret-key-for-script"
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "local"

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.db.database import AsyncSessionLocal
from app.db.models import Game, League, LeagueMember, Prediction, User
from app.db.models.game import GameStatus
from app.services.scoring_service import calculate_prediction_points, score_all_predictions_for_game

BACKEND_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = BACKEND_ROOT / ".matrix_demo_snapshot.json"

DEMO_LEAGUE_PREFIX = "[LOCAL MATRIX DEMO]"
DEMO_EMAIL_PREFIX = "matrixdemo+"
DEMO_EMAIL_SUFFIX = "@local.predico.invalid"
DEMO_PASSWORD = "matrixdemo-local-only"
DEFAULT_GAME_COUNT = 20
DEFAULT_MEMBER_COUNT = 10

MATRIX_POINT_TARGETS = (100, 65, 50, 15, 0)

PRODUCTION_DATABASE_MARKERS = (
    "herokuapp.com",
    "heroku.com",
    "amazonaws.com",
    ".rds.",
    "elephantsql.com",
)

DEMO_USERNAMES = [
    "MatrixAce",
    "CellCarla",
    "GridGabe",
    "RowRiley",
    "ColCasey",
    "MatchMorgan",
    "PointsPia",
    "ScoreSky",
    "TableTess",
    "ViewVince",
]


def assert_localhost_only(confirm_local: bool) -> None:
    if not confirm_local:
        print("ERROR: Pass --confirm-local to acknowledge this only runs on local Docker Postgres.")
        sys.exit(1)

    if os.getenv("DYNO"):
        print("ERROR: Refusing to run on Heroku (DYNO is set).")
        sys.exit(1)

    environment = os.getenv("ENVIRONMENT", "local").lower()
    if environment in {"production", "staging"}:
        print(f"ERROR: Refusing to run with ENVIRONMENT={environment}.")
        sys.exit(1)

    database_url = os.getenv("DATABASE_URL", "").lower()
    if not database_url:
        print("ERROR: DATABASE_URL is not set.")
        sys.exit(1)

    if any(marker in database_url for marker in PRODUCTION_DATABASE_MARKERS):
        print("ERROR: DATABASE_URL looks like a hosted/production database.")
        sys.exit(1)

    local_markers = ("localhost", "127.0.0.1", "@postgres:", "predico_user:predico_password@postgres")
    if not any(marker in database_url for marker in local_markers):
        print("ERROR: DATABASE_URL must point at local Docker Postgres (postgres service or localhost).")
        sys.exit(1)


def demo_email(suffix: str) -> str:
    return f"{DEMO_EMAIL_PREFIX}{suffix}{DEMO_EMAIL_SUFFIX}"


def game_to_snapshot(game: Game) -> dict[str, Any]:
    return {
        "id": game.id,
        "status": game.status.value,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "home_penalty_score": game.home_penalty_score,
        "away_penalty_score": game.away_penalty_score,
        "scheduled_at": game.scheduled_at.isoformat() if game.scheduled_at else None,
        "match_date": game.match_date.isoformat() if game.match_date else None,
        "match_time": game.match_time.isoformat() if game.match_time else None,
    }


def apply_game_snapshot(game: Game, data: dict[str, Any]) -> None:
    game.status = GameStatus(data["status"])
    game.home_score = data["home_score"]
    game.away_score = data["away_score"]
    game.home_penalty_score = data["home_penalty_score"]
    game.away_penalty_score = data["away_penalty_score"]
    game.scheduled_at = datetime.fromisoformat(data["scheduled_at"]) if data["scheduled_at"] else game.scheduled_at
    game.match_date = date.fromisoformat(data["match_date"]) if data.get("match_date") else game.match_date
    game.match_time = time.fromisoformat(data["match_time"]) if data.get("match_time") else game.match_time


def pick_prediction_for_target(
    actual_home: int,
    actual_away: int,
    target_points: int,
) -> tuple[int, int]:
    for predicted_home in range(0, 6):
        for predicted_away in range(0, 6):
            points, _ = calculate_prediction_points(
                predicted_home,
                predicted_away,
                actual_home,
                actual_away,
            )
            if points == target_points:
                return predicted_home, predicted_away

    return (actual_home, actual_away) if target_points == 100 else (0, 3)


async def load_first_games(db, count: int) -> list[Game]:
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.home_team), selectinload(Game.away_team))
        .order_by(
            Game.match_date.asc().nulls_last(),
            Game.match_time.asc().nulls_last(),
            Game.scheduled_at.asc(),
            Game.id.asc(),
        )
        .limit(count)
    )
    games = list(result.scalars().all())
    if len(games) < count:
        raise RuntimeError(
            f"Need at least {count} games in the database. "
            "Run populate_world_cup_data.py locally first."
        )
    return games


async def get_demo_league(db) -> League | None:
    result = await db.execute(
        select(League).where(League.name.like(f"{DEMO_LEAGUE_PREFIX}%")).limit(1)
    )
    return result.scalar_one_or_none()


async def get_demo_users(db) -> list[User]:
    result = await db.execute(select(User).where(User.email.like(f"{DEMO_EMAIL_PREFIX}%{DEMO_EMAIL_SUFFIX}")))
    return list(result.scalars().all())


async def remove_demo_data(db) -> None:
    if not SNAPSHOT_PATH.exists():
        demo_league = await get_demo_league(db)
        demo_users = await get_demo_users(db)
        if not demo_league and not demo_users:
            print("No matrix demo data found.")
            return
        print("WARNING: Snapshot file missing; will remove demo users/league but cannot restore games.")

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")) if SNAPSHOT_PATH.exists() else None
    game_ids = snapshot["game_ids"] if snapshot else []

    demo_users = await get_demo_users(db)
    demo_user_ids = [user.id for user in demo_users]

    if game_ids and demo_user_ids:
        await db.execute(
            delete(Prediction).where(
                Prediction.game_id.in_(game_ids),
                Prediction.user_id.in_(demo_user_ids),
            )
        )

    demo_league = await get_demo_league(db)
    if demo_league:
        await db.execute(delete(LeagueMember).where(LeagueMember.league_id == demo_league.id))
        await db.execute(delete(League).where(League.id == demo_league.id))

    if demo_user_ids:
        await db.execute(delete(User).where(User.id.in_(demo_user_ids)))

    if snapshot:
        games_result = await db.execute(select(Game).where(Game.id.in_(game_ids)))
        games_by_id = {game.id: game for game in games_result.scalars().all()}
        for item in snapshot["games"]:
            game = games_by_id.get(item["id"])
            if game:
                apply_game_snapshot(game, item)

    await db.commit()

    if SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.unlink()

    print("Removed matrix demo league/users and restored modified games.")


async def seed_demo_data(db, *, game_count: int, join_email: str | None) -> None:
    if SNAPSHOT_PATH.exists():
        print("Matrix demo snapshot already exists. Run with --remove first, or use --force to recreate.")
        sys.exit(1)

    existing = await get_demo_league(db)
    if existing:
        print("Matrix demo league already exists. Run with --remove first.")
        sys.exit(1)

    games = await load_first_games(db, game_count)
    modified_snapshots: list[dict[str, Any]] = []
    base_day = datetime.utcnow() - timedelta(days=game_count + 3)

    for index, game in enumerate(games):
        if game.status != GameStatus.FINISHED:
            modified_snapshots.append(game_to_snapshot(game))

        kickoff = base_day + timedelta(days=index, hours=18)
        game.status = GameStatus.FINISHED
        if game.home_score is None or game.away_score is None:
            game.home_score = (index + 1) % 4
            game.away_score = index % 3
        game.home_penalty_score = None
        game.away_penalty_score = None
        game.scheduled_at = kickoff
        game.match_date = kickoff.date()
        game.match_time = time(kickoff.hour, kickoff.minute)

    if modified_snapshots:
        SNAPSHOT_PATH.write_text(
            json.dumps(
                {
                    "game_ids": [item["id"] for item in modified_snapshots],
                    "games": modified_snapshots,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    password_hash = get_password_hash(DEMO_PASSWORD)
    demo_users: list[User] = []
    used_suffixes: set[str] = set()

    for username in DEMO_USERNAMES[:DEFAULT_MEMBER_COUNT]:
        suffix = secrets.token_hex(3)
        while suffix in used_suffixes:
            suffix = secrets.token_hex(3)
        used_suffixes.add(suffix)

        user = User(
            email=demo_email(suffix),
            username=username,
            hashed_password=password_hash,
            email_verified=True,
            is_active=True,
        )
        db.add(user)
        demo_users.append(user)

    await db.flush()

    creator = demo_users[0]
    league = League(
        name=f"{DEMO_LEAGUE_PREFIX} Progress matrix test league",
        description="Local-only demo data for matrix progress testing. Safe to delete with seed_matrix_demo.py --remove.",
        created_by=creator.id,
        is_private=False,
        invite_code=None,
    )
    db.add(league)
    await db.flush()

    member_users: list[User] = list(demo_users)
    if join_email:
        join_result = await db.execute(select(User).where(User.email == join_email.lower()))
        join_user = join_result.scalar_one_or_none()
        if not join_user:
            raise RuntimeError(f"No local user found with email {join_email}")
        if join_user not in member_users:
            member_users.append(join_user)

    for member in member_users:
        db.add(LeagueMember(league_id=league.id, user_id=member.id, total_points=0))

    for member_index, member in enumerate(member_users):
        for game_index, game in enumerate(games):
            target_points = MATRIX_POINT_TARGETS[(member_index + game_index) % len(MATRIX_POINT_TARGETS)]
            predicted_home, predicted_away = pick_prediction_for_target(
                game.home_score or 0,
                game.away_score or 0,
                target_points,
            )
            existing_result = await db.execute(
                select(Prediction).where(
                    Prediction.user_id == member.id,
                    Prediction.game_id == game.id,
                )
            )
            existing = existing_result.scalar_one_or_none()
            if existing:
                existing.predicted_home_score = predicted_home
                existing.predicted_away_score = predicted_away
                existing.points = 0
                existing.exact_score_points = 0
                existing.correct_result_points = 0
                existing.correct_goal_difference_points = 0
                existing.is_calculated = False
            else:
                db.add(
                    Prediction(
                        user_id=member.id,
                        game_id=game.id,
                        predicted_home_score=predicted_home,
                        predicted_away_score=predicted_away,
                        points=0,
                        is_calculated=False,
                    )
                )

    await db.flush()

    for game in games:
        refreshed = await db.execute(
            select(Game)
            .where(Game.id == game.id)
            .options(selectinload(Game.home_team), selectinload(Game.away_team))
        )
        finished_game = refreshed.scalar_one()
        await score_all_predictions_for_game(finished_game, db)

    await db.commit()

    print("")
    print("Matrix demo seeded successfully (LOCAL ONLY).")
    print(f"  League name: {league.name}")
    print(f"  League URL:  /leagues/{league.public_id}")
    print(f"  Members:     {len(member_users)} (demo password for fake users: {DEMO_PASSWORD})")
    print(f"  Matches:     first {game_count} games scored; every member has a prediction on each")
    print("")
    print("Next steps:")
    print("  1. Enable chart flag: docker compose exec backend python scripts/feature_flags.py league-progress-chart on")
    print("  2. docker compose restart backend")
    print("  3. Open the league URL above and watch the progress preview rotate to the matrix")
    print("")
    print("To undo everything:")
    print("  docker compose exec backend python scripts/seed_matrix_demo.py --confirm-local --remove")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed or remove LOCAL-ONLY league matrix demo data.")
    parser.add_argument(
        "--confirm-local",
        action="store_true",
        help="Required safety flag — confirms you are on local Docker Postgres only.",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove demo league/users and restore modified games from snapshot.",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=DEFAULT_GAME_COUNT,
        help=f"Number of opening matches to include (default {DEFAULT_GAME_COUNT}).",
    )
    parser.add_argument(
        "--join-email",
        help="Optional existing local user email to add to the demo league (e.g. your account).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --remove, clean up first then seed again.",
    )
    args = parser.parse_args()

    assert_localhost_only(args.confirm_local)

    async with AsyncSessionLocal() as db:
        if args.remove:
            await remove_demo_data(db)
            if not args.force:
                return

        if args.force and not args.remove:
            await remove_demo_data(db)

        await seed_demo_data(db, game_count=args.games, join_email=args.join_email)


if __name__ == "__main__":
    asyncio.run(main())
