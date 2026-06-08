"""
Seed ghost users and sample leagues to make the platform feel active on browse pages.

Ghost users:
  - Email: rafaelalfredo2008+<8 hex chars>@gmail.com (Gmail plus-addressing; not shown in UI)
  - email_verified=True, no verification emails sent
  - Realistic usernames (not derived from email)

Ghost leagues:
  - Private with random passwords (visible in browse with member counts, not joinable by accident)
  - 10–13 leagues, each with 4–7 ghost members and random leaderboard points

Usage (local Docker):
  docker compose exec backend python scripts/seed_ghost_activity.py

Usage (Heroku production — run once):
  heroku run python scripts/seed_ghost_activity.py -a predico-api

Remove all ghost data:
  python scripts/seed_ghost_activity.py --remove

Re-create from scratch:
  python scripts/seed_ghost_activity.py --remove
  python scripts/seed_ghost_activity.py
"""
import argparse
import asyncio
import os
import random
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db"
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-secret-key-for-script"

from sqlalchemy import delete, func, select

from app.core.security import get_password_hash
from app.db.database import AsyncSessionLocal
from app.db.models import League, LeagueMember, User

GHOST_EMAIL_PREFIX = "rafaelalfredo2008+"
GHOST_EMAIL_SUFFIX = "@gmail.com"
TARGET_GHOST_USERS = 50
TARGET_LEAGUE_COUNT = (10, 13)
MEMBERS_PER_LEAGUE = (4, 7)

GHOST_USERNAMES = [
    "AndersL", "BjornKicks", "CalleOffside", "DianaXI", "Eriksson88",
    "FridaGol", "GustavTactics", "HannaCorner", "IsakPress", "JohanSetPiece",
    "KarinDerby", "LarsMidfield", "MajaStriker", "NilsKeeper", "OliviaForm",
    "Pettersson", "QuinnVolley", "RebeccaUltras", "SimonScout", "TuvaMatchday",
    "UlrikFan", "ViktorCup", "WilmaPredict", "AxelAggregate", "BeatriceBoost",
    "CorneliusClean", "EbbaExtra", "FelixFixture", "GretaGroup", "HenrikHattrick",
    "IngridInbox", "JoelJoker", "KlaraKickoff", "LeoLineup", "MoaMatchweek",
    "NoahNutmeg", "PetraPenalty", "RasmusRound", "SaraScorer", "TobiasTable",
    "UllaUnderdog", "VeraVictory", "WilliamWall", "YlvaYellow", "ZachZone",
    "AlmaArena", "BrunoBrace", "CeciliaChip", "DavidDraw", "ElinEleven",
]

LEAGUE_TEMPLATES = [
    ("Stockholm Office Pool", "Weekly banter and questionable predictions."),
    ("Gothenburg Fanatics", "West coast pride on the line."),
    ("Malmö Monday Club", "Lunch-break league, serious-ish."),
    ("Norrköping Night Owls", "Late kickoffs welcome."),
    ("Uppsala Uni Alumni", "Old classmates, new scores."),
    ("Lund Lab League", "PhD stress relief via football."),
    ("Helsinki Harbour Pool", "Cross-border friendly rivalry."),
    ("Oslo Overlap Eleven", "Scandi derby energy."),
    ("Copenhagen Corner Crew", "Hyggelig but competitive."),
    ("Berlin Bridge Buddies", "Expat crowd from last World Cup."),
    ("London Lunch League", "Remote workers united."),
    ("Dublin Dubs Pool", "Guinness-adjacent predictions."),
    ("Barcelona Brunch XI", "Sun, tapas, wrong scores."),
]


def ghost_email(local_suffix: str) -> str:
    return f"{GHOST_EMAIL_PREFIX}{local_suffix}{GHOST_EMAIL_SUFFIX}"


def is_ghost_email(email: str) -> bool:
    return (
        email.startswith(GHOST_EMAIL_PREFIX)
        and email.endswith(GHOST_EMAIL_SUFFIX)
        and len(email) > len(GHOST_EMAIL_PREFIX) + len(GHOST_EMAIL_SUFFIX)
    )


async def count_ghost_users(db) -> int:
    result = await db.execute(
        select(func.count()).select_from(User).where(User.email.like(f"{GHOST_EMAIL_PREFIX}%{GHOST_EMAIL_SUFFIX}"))
    )
    return int(result.scalar_one())


async def get_ghost_user_ids(db) -> list[int]:
    result = await db.execute(
        select(User.id).where(User.email.like(f"{GHOST_EMAIL_PREFIX}%{GHOST_EMAIL_SUFFIX}"))
    )
    return [row[0] for row in result.all()]


async def remove_ghost_data(db) -> None:
    ghost_ids = await get_ghost_user_ids(db)
    if not ghost_ids:
        print("No ghost users found.")
        return

    league_ids_result = await db.execute(select(League.id).where(League.created_by.in_(ghost_ids)))
    league_ids = [row[0] for row in league_ids_result.all()]

    if league_ids:
        await db.execute(delete(LeagueMember).where(LeagueMember.league_id.in_(league_ids)))
        await db.execute(delete(League).where(League.id.in_(league_ids)))

    await db.execute(delete(User).where(User.id.in_(ghost_ids)))
    await db.commit()
    print(f"Removed {len(ghost_ids)} ghost users and {len(league_ids)} ghost leagues.")


async def seed_ghost_users(db) -> list[User]:
    existing_count = await count_ghost_users(db)
    if existing_count >= TARGET_GHOST_USERS:
        print(f"Already have {existing_count} ghost users (target {TARGET_GHOST_USERS}). Skipping user creation.")
        result = await db.execute(
            select(User).where(User.email.like(f"{GHOST_EMAIL_PREFIX}%{GHOST_EMAIL_SUFFIX}"))
        )
        return list(result.scalars().all())

    used_usernames_result = await db.execute(select(User.username))
    used_usernames = {row[0] for row in used_usernames_result.all()}

    available_names = [name for name in GHOST_USERNAMES if name not in used_usernames]
    needed = TARGET_GHOST_USERS - existing_count
    if len(available_names) < needed:
        raise RuntimeError(
            f"Need {needed} usernames but only {len(available_names)} available from the built-in list."
        )

    random.shuffle(available_names)
    password_hash = get_password_hash(secrets.token_urlsafe(32))
    created: list[User] = []

    for username in available_names[:needed]:
        local_suffix = secrets.token_hex(4)
        email = ghost_email(local_suffix)
        user = User(
            email=email,
            username=username,
            hashed_password=password_hash,
            email_verified=True,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(7, 90)),
        )
        db.add(user)
        created.append(user)

    await db.flush()
    await db.commit()
    print(f"Created {len(created)} ghost users.")

    result = await db.execute(
        select(User).where(User.email.like(f"{GHOST_EMAIL_PREFIX}%{GHOST_EMAIL_SUFFIX}"))
    )
    return list(result.scalars().all())


async def seed_ghost_leagues(db, ghost_users: list[User]) -> None:
    ghost_ids = {user.id for user in ghost_users}
    existing_leagues = await db.execute(select(League).where(League.created_by.in_(ghost_ids)))
    if existing_leagues.scalars().first():
        print("Ghost leagues already exist. Skipping league creation (use --remove first to recreate).")
        return

    league_count = random.randint(*TARGET_LEAGUE_COUNT)
    templates = random.sample(LEAGUE_TEMPLATES, k=min(league_count, len(LEAGUE_TEMPLATES)))

    for index, (name, description) in enumerate(templates[:league_count]):
        creator = random.choice(ghost_users)
        invite_code = secrets.token_urlsafe(9)
        league = League(
            name=name,
            description=description,
            created_by=creator.id,
            is_private=True,
            invite_code=invite_code,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
        )
        db.add(league)
        await db.flush()

        member_count = random.randint(*MEMBERS_PER_LEAGUE)
        members = random.sample(ghost_users, k=min(member_count, len(ghost_users)))
        if creator not in members:
            members[0] = creator

        for member_user in members:
            points = random.randint(0, 85)
            db.add(
                LeagueMember(
                    league_id=league.id,
                    user_id=member_user.id,
                    total_points=points,
                    joined_at=league.created_at + timedelta(hours=random.randint(1, 72)),
                )
            )

    await db.commit()
    print(f"Created {league_count} private ghost leagues with {MEMBERS_PER_LEAGUE[0]}–{MEMBERS_PER_LEAGUE[1]} members each.")


async def main(remove: bool, seed: bool) -> None:
    async with AsyncSessionLocal() as db:
        if remove:
            await remove_ghost_data(db)
            if not seed:
                return

        if seed:
            ghost_users = await seed_ghost_users(db)
            await seed_ghost_leagues(db, ghost_users)
            user_count = await count_ghost_users(db)
            ghost_ids = await get_ghost_user_ids(db)
            league_count_result = await db.execute(
                select(func.count()).select_from(League).where(League.created_by.in_(ghost_ids))
            )
            league_count = int(league_count_result.scalar_one())
            print(f"Done. Ghost users: {user_count}, ghost leagues: {league_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed or remove ghost activity for Predico.")
    parser.add_argument("--remove", action="store_true", help="Delete all ghost users and their leagues.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove existing ghost data, then create fresh seed data.",
    )
    args = parser.parse_args()

    if args.force:
        asyncio.run(main(remove=True, seed=True))
    elif args.remove:
        asyncio.run(main(remove=True, seed=False))
    else:
        asyncio.run(main(remove=False, seed=True))
