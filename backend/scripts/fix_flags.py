"""
Script to fix incorrect flag emojis in the database.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set default environment variables if not set (for local development)
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db'
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-for-script'

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models.team import Team

# Correct flag emojis
# Note: Scotland doesn't have a standard Unicode flag emoji, so we'll use a text representation or the UK flag
FLAG_FIXES = {
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',  # Scotland flag (tag sequence)
    'Paraguay': '🇵🇾',  # Paraguay flag (PY)
    'Curaçao': '🇨🇼',  # Curaçao flag (CW)
    'Cape Verde': '🇨🇻',  # Cape Verde flag (CV)
    'Uruguay': '🇺🇾',  # Uruguay flag (UY)
    'Austria': '🇦🇹',  # Austria flag (AT) - NOT Australia (AU)
    'S. Africa': '🇿🇦',  # South Africa flag (ZA)
    'South Africa': '🇿🇦',  # South Africa flag (also update the old name)
}

# Team name updates
NAME_UPDATES = {
    'South Africa': 'S. Africa',
}


async def fix_flags_and_names():
    """Fix flag emojis and team names in the database."""
    print("=" * 80)
    print("Fixing Flag Emojis and Team Names")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as session:
        # Update team names first
        print("Updating team names...")
        for old_name, new_name in NAME_UPDATES.items():
            result = await session.execute(
                select(Team).where(Team.name == old_name)
            )
            team = result.scalar_one_or_none()
            if team:
                team.name = new_name
                print(f"  Updated: {old_name} → {new_name}")
        
        await session.commit()
        
        # Update flags
        print("\nUpdating flag emojis...")
        for team_name, correct_flag in FLAG_FIXES.items():
            result = await session.execute(
                select(Team).where(Team.name == team_name)
            )
            team = result.scalar_one_or_none()
            if team:
                if team.flag_emoji != correct_flag:
                    old_flag = team.flag_emoji or '(none)'
                    team.flag_emoji = correct_flag
                    print(f"  Updated {team_name}: {old_flag} → {correct_flag}")
                else:
                    print(f"  {team_name}: Already correct ({correct_flag})")
            else:
                print(f"  WARNING: Team '{team_name}' not found")
        
        await session.commit()
        print("\n✓ Flag and name fixes complete!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(fix_flags_and_names())

