"""
Script to populate database with official 2026 FIFA World Cup data.
Includes teams, groups, rounds, and group stage matches.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, date, time
from typing import Dict, List, Tuple

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set default environment variables if not set (for local development)
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db'
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-for-script'

from sqlalchemy import select, delete, text as sa_text
from sqlalchemy.orm import selectinload
from app.db.database import AsyncSessionLocal
from app.db.models.team import Team
from app.db.models.group import Group, GroupTeam
from app.db.models.round import Round, RoundType
from app.db.models.game import Game, GameStatus

# Country code to flag emoji mapping
# Using ISO 3166-1 alpha-3 country codes
COUNTRY_FLAGS = {
    'MEX': '🇲🇽', 'ZAF': '🇿🇦', 'KOR': '🇰🇷', 'IRL': '🇮🇪',
    'CAN': '🇨🇦', 'ITA': '🇮🇹', 'QAT': '🇶🇦', 'CHE': '🇨🇭',
    'BRA': '🇧🇷', 'MAR': '🇲🇦', 'HTI': '🇭🇹', 'SCO': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',  # Scotland flag
    'USA': '🇺🇸', 'PRY': '🇵🇾', 'AUS': '🇦🇺', 'ROU': '🇷🇴',
    'DEU': '🇩🇪', 'CUW': '🇨🇼', 'CIV': '🇨🇮', 'ECU': '🇪🇨',
    'NLD': '🇳🇱', 'JPN': '🇯🇵', 'SWE': '🇸🇪', 'TUN': '🇹🇳',
    'BEL': '🇧🇪', 'EGY': '🇪🇬', 'IRN': '🇮🇷', 'NZL': '🇳🇿',
    'ESP': '🇪🇸', 'CPV': '🇨🇻', 'SAU': '🇸🇦', 'URY': '🇺🇾',
    'FRA': '🇫🇷', 'SEN': '🇸🇳', 'IRQ': '🇮🇶', 'NOR': '🇳🇴',
    'ARG': '🇦🇷', 'DZA': '🇩🇿', 'AUT': '🇦🇹', 'JOR': '🇯🇴',
    'PRT': '🇵🇹', 'COD': '🇨🇩', 'UZB': '🇺🇿', 'COL': '🇨🇴',
    'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'HRV': '🇭🇷', 'GHA': '🇬🇭', 'PAN': '🇵🇦',
}

# Official 2026 World Cup Groups
GROUPS_DATA = {
    'A': ['Mexico', 'S. Africa', 'South Korea', 'Ireland'],
    'B': ['Canada', 'Italy', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'D': ['United States', 'Paraguay', 'Australia', 'Romania'],
    'E': ['Germany', 'Curaçao', 'Ivory Coast', 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

# Country name to country code mapping
COUNTRY_CODES = {
    'Mexico': 'MEX', 'South Africa': 'ZAF', 'S. Africa': 'ZAF', 'South Korea': 'KOR', 'Ireland': 'IRL',
    'Canada': 'CAN', 'Italy': 'ITA', 'Qatar': 'QAT', 'Switzerland': 'CHE',
    'Brazil': 'BRA', 'Morocco': 'MAR', 'Haiti': 'HTI', 'Scotland': 'SCO',
    'United States': 'USA', 'Paraguay': 'PRY', 'Australia': 'AUS', 'Romania': 'ROU',
    'Germany': 'DEU', 'Curaçao': 'CUW', 'Ivory Coast': 'CIV', 'Ecuador': 'ECU',
    'Netherlands': 'NLD', 'Japan': 'JPN', 'Sweden': 'SWE', 'Tunisia': 'TUN',
    'Belgium': 'BEL', 'Egypt': 'EGY', 'Iran': 'IRN', 'New Zealand': 'NZL',
    'Spain': 'ESP', 'Cape Verde': 'CPV', 'Saudi Arabia': 'SAU', 'Uruguay': 'URY',
    'France': 'FRA', 'Senegal': 'SEN', 'Iraq': 'IRQ', 'Norway': 'NOR',
    'Argentina': 'ARG', 'Algeria': 'DZA', 'Austria': 'AUT', 'Jordan': 'JOR',
    'Portugal': 'PRT', 'DR Congo': 'COD', 'Uzbekistan': 'UZB', 'Colombia': 'COL',
    'England': 'ENG', 'Croatia': 'HRV', 'Ghana': 'GHA', 'Panama': 'PAN',
}

# Round definitions
ROUNDS_DATA = [
    # Group stage matchdays
    {'name': 'Matchday 1', 'type': RoundType.GROUP_STAGE, 'order': 1},
    {'name': 'Matchday 2', 'type': RoundType.GROUP_STAGE, 'order': 2},
    {'name': 'Matchday 3', 'type': RoundType.GROUP_STAGE, 'order': 3},
    # Knockout rounds
    {'name': 'Round of 32', 'type': RoundType.ROUND_OF_32, 'order': 4},
    {'name': 'Round of 16', 'type': RoundType.ROUND_OF_16, 'order': 5},
    {'name': 'Quarterfinals', 'type': RoundType.QUARTER_FINALS, 'order': 6},
    {'name': 'Semifinals', 'type': RoundType.SEMI_FINALS, 'order': 7},
    {'name': 'Third Place', 'type': RoundType.THIRD_PLACE, 'order': 8},
    {'name': 'Final', 'type': RoundType.FINAL, 'order': 9},
]

# Matchday date ranges (from Wikipedia Match Schedule section)
MATCHDAY_DATES = {
    'Matchday 1': (date(2026, 6, 11), date(2026, 6, 17)),
    'Matchday 2': (date(2026, 6, 18), date(2026, 6, 24)),
    'Matchday 3': (date(2026, 6, 25), date(2026, 7, 1)),
}

# Group stage matches with dates
# Format: (group, home_team, away_team, match_date, matchday)
# Dates extracted from Wikipedia group stage section
GROUP_STAGE_MATCHES = [
    # Group A
    ('A', 'Mexico', 'S. Africa', date(2026, 6, 11), 'Matchday 1'),
    ('A', 'South Korea', 'Ireland', date(2026, 6, 11), 'Matchday 1'),
    ('A', 'S. Africa', 'Ireland', date(2026, 6, 19), 'Matchday 2'),
    ('A', 'Mexico', 'South Korea', date(2026, 6, 19), 'Matchday 2'),
    ('A', 'Ireland', 'Mexico', date(2026, 6, 28), 'Matchday 3'),
    ('A', 'S. Africa', 'South Korea', date(2026, 6, 28), 'Matchday 3'),
    
    # Group B
    ('B', 'Canada', 'Italy', date(2026, 6, 12), 'Matchday 1'),
    ('B', 'Qatar', 'Switzerland', date(2026, 6, 12), 'Matchday 1'),
    ('B', 'Italy', 'Switzerland', date(2026, 6, 20), 'Matchday 2'),
    ('B', 'Canada', 'Qatar', date(2026, 6, 20), 'Matchday 2'),
    ('B', 'Switzerland', 'Canada', date(2026, 6, 29), 'Matchday 3'),
    ('B', 'Italy', 'Qatar', date(2026, 6, 29), 'Matchday 3'),
    
    # Group C
    ('C', 'Brazil', 'Morocco', date(2026, 6, 12), 'Matchday 1'),
    ('C', 'Haiti', 'Scotland', date(2026, 6, 12), 'Matchday 1'),
    ('C', 'Morocco', 'Scotland', date(2026, 6, 20), 'Matchday 2'),
    ('C', 'Brazil', 'Haiti', date(2026, 6, 20), 'Matchday 2'),
    ('C', 'Scotland', 'Brazil', date(2026, 6, 29), 'Matchday 3'),
    ('C', 'Morocco', 'Haiti', date(2026, 6, 29), 'Matchday 3'),
    
    # Group D
    ('D', 'United States', 'Paraguay', date(2026, 6, 12), 'Matchday 1'),
    ('D', 'Australia', 'Romania', date(2026, 6, 12), 'Matchday 1'),
    ('D', 'Paraguay', 'Romania', date(2026, 6, 21), 'Matchday 2'),
    ('D', 'United States', 'Australia', date(2026, 6, 21), 'Matchday 2'),
    ('D', 'Romania', 'United States', date(2026, 6, 30), 'Matchday 3'),
    ('D', 'Paraguay', 'Australia', date(2026, 6, 30), 'Matchday 3'),
    
    # Group E
    ('E', 'Germany', 'Curaçao', date(2026, 6, 13), 'Matchday 1'),
    ('E', 'Ivory Coast', 'Ecuador', date(2026, 6, 13), 'Matchday 1'),
    ('E', 'Curaçao', 'Ecuador', date(2026, 6, 21), 'Matchday 2'),
    ('E', 'Germany', 'Ivory Coast', date(2026, 6, 21), 'Matchday 2'),
    ('E', 'Ecuador', 'Germany', date(2026, 6, 30), 'Matchday 3'),
    ('E', 'Curaçao', 'Ivory Coast', date(2026, 6, 30), 'Matchday 3'),
    
    # Group F
    ('F', 'Netherlands', 'Japan', date(2026, 6, 13), 'Matchday 1'),
    ('F', 'Sweden', 'Tunisia', date(2026, 6, 13), 'Matchday 1'),
    ('F', 'Japan', 'Tunisia', date(2026, 6, 22), 'Matchday 2'),
    ('F', 'Netherlands', 'Sweden', date(2026, 6, 22), 'Matchday 2'),
    ('F', 'Tunisia', 'Netherlands', date(2026, 7, 1), 'Matchday 3'),
    ('F', 'Japan', 'Sweden', date(2026, 7, 1), 'Matchday 3'),
    
    # Group G
    ('G', 'Belgium', 'Egypt', date(2026, 6, 14), 'Matchday 1'),
    ('G', 'Iran', 'New Zealand', date(2026, 6, 14), 'Matchday 1'),
    ('G', 'Egypt', 'New Zealand', date(2026, 6, 22), 'Matchday 2'),
    ('G', 'Belgium', 'Iran', date(2026, 6, 22), 'Matchday 2'),
    ('G', 'New Zealand', 'Belgium', date(2026, 7, 1), 'Matchday 3'),
    ('G', 'Egypt', 'Iran', date(2026, 7, 1), 'Matchday 3'),
    
    # Group H
    ('H', 'Spain', 'Cape Verde', date(2026, 6, 14), 'Matchday 1'),
    ('H', 'Saudi Arabia', 'Uruguay', date(2026, 6, 14), 'Matchday 1'),
    ('H', 'Cape Verde', 'Uruguay', date(2026, 6, 23), 'Matchday 2'),
    ('H', 'Spain', 'Saudi Arabia', date(2026, 6, 23), 'Matchday 2'),
    ('H', 'Uruguay', 'Spain', date(2026, 7, 1), 'Matchday 3'),
    ('H', 'Cape Verde', 'Saudi Arabia', date(2026, 7, 1), 'Matchday 3'),
    
    # Group I
    ('I', 'France', 'Senegal', date(2026, 6, 15), 'Matchday 1'),
    ('I', 'Iraq', 'Norway', date(2026, 6, 15), 'Matchday 1'),
    ('I', 'Senegal', 'Norway', date(2026, 6, 23), 'Matchday 2'),
    ('I', 'France', 'Iraq', date(2026, 6, 23), 'Matchday 2'),
    ('I', 'Norway', 'France', date(2026, 7, 1), 'Matchday 3'),
    ('I', 'Senegal', 'Iraq', date(2026, 7, 1), 'Matchday 3'),
    
    # Group J
    ('J', 'Argentina', 'Algeria', date(2026, 6, 15), 'Matchday 1'),
    ('J', 'Austria', 'Jordan', date(2026, 6, 15), 'Matchday 1'),
    ('J', 'Algeria', 'Jordan', date(2026, 6, 24), 'Matchday 2'),
    ('J', 'Argentina', 'Austria', date(2026, 6, 24), 'Matchday 2'),
    ('J', 'Jordan', 'Argentina', date(2026, 7, 1), 'Matchday 3'),
    ('J', 'Algeria', 'Austria', date(2026, 7, 1), 'Matchday 3'),
    
    # Group K
    ('K', 'Portugal', 'DR Congo', date(2026, 6, 16), 'Matchday 1'),
    ('K', 'Uzbekistan', 'Colombia', date(2026, 6, 16), 'Matchday 1'),
    ('K', 'DR Congo', 'Colombia', date(2026, 6, 24), 'Matchday 2'),
    ('K', 'Portugal', 'Uzbekistan', date(2026, 6, 24), 'Matchday 2'),
    ('K', 'Colombia', 'Portugal', date(2026, 7, 1), 'Matchday 3'),
    ('K', 'DR Congo', 'Uzbekistan', date(2026, 7, 1), 'Matchday 3'),
    
    # Group L
    ('L', 'England', 'Croatia', date(2026, 6, 16), 'Matchday 1'),
    ('L', 'Ghana', 'Panama', date(2026, 6, 16), 'Matchday 1'),
    ('L', 'Croatia', 'Panama', date(2026, 6, 25), 'Matchday 2'),
    ('L', 'England', 'Ghana', date(2026, 6, 25), 'Matchday 2'),
    ('L', 'Panama', 'England', date(2026, 7, 1), 'Matchday 3'),
    ('L', 'Croatia', 'Ghana', date(2026, 7, 1), 'Matchday 3'),
]


async def create_teams(session):
    """Create all teams in the database."""
    print("Creating teams...")
    teams_created = 0
    teams_updated = 0
    
    all_teams = set()
    for group_teams in GROUPS_DATA.values():
        all_teams.update(group_teams)
    
    for team_name in sorted(all_teams):
        country_code = COUNTRY_CODES.get(team_name)
        flag_emoji = COUNTRY_FLAGS.get(country_code, '🏳️')
        
        if not country_code:
            print(f"  WARNING: No country code found for {team_name}")
            continue
        
        # Check if team exists
        result = await session.execute(
            select(Team).where(Team.name == team_name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update if needed
            updated = False
            if existing.country_code != country_code:
                existing.country_code = country_code
                updated = True
            if existing.flag_emoji != flag_emoji:
                existing.flag_emoji = flag_emoji
                updated = True
            if updated:
                teams_updated += 1
                print(f"  Updated: {team_name} ({country_code}) {flag_emoji}")
        else:
            # Create new team
            new_team = Team(
                name=team_name,
                country_code=country_code,
                flag_emoji=flag_emoji
            )
            session.add(new_team)
            teams_created += 1
            print(f"  Created: {team_name} ({country_code}) {flag_emoji}")
    
    await session.commit()
    print(f"✓ Teams: {teams_created} created, {teams_updated} updated\n")
    return teams_created + teams_updated


async def create_groups(session):
    """Create all groups in the database."""
    print("Creating groups...")
    groups_created = 0
    
    for group_letter in sorted(GROUPS_DATA.keys()):
        group_name = f"Group {group_letter}"
        
        result = await session.execute(
            select(Group).where(Group.name == group_name)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            new_group = Group(name=group_name)
            session.add(new_group)
            groups_created += 1
            print(f"  Created: {group_name}")
    
    await session.commit()
    print(f"✓ Groups: {groups_created} created\n")
    return groups_created


async def link_teams_to_groups(session):
    """Link teams to their respective groups."""
    print("Linking teams to groups...")
    links_created = 0
    links_skipped = 0
    
    # Get all teams and groups
    teams_result = await session.execute(select(Team))
    teams = {team.name: team for team in teams_result.scalars().all()}
    
    groups_result = await session.execute(select(Group))
    groups = {group.name: group for group in groups_result.scalars().all()}
    
    # Clear existing group_teams for these groups (optional - comment out if you want to keep old data)
    # for group_name in groups.keys():
    #     group = groups[group_name]
    #     await session.execute(delete(GroupTeam).where(GroupTeam.group_id == group.id))
    
    for group_letter, team_names in GROUPS_DATA.items():
        group_name = f"Group {group_letter}"
        group = groups.get(group_name)
        
        if not group:
            print(f"  WARNING: Group {group_name} not found")
            continue
        
        for team_name in team_names:
            team = teams.get(team_name)
            if not team:
                print(f"  WARNING: Team {team_name} not found")
                continue
            
            # Check if link already exists
            result = await session.execute(
                select(GroupTeam).where(
                    GroupTeam.group_id == group.id,
                    GroupTeam.team_id == team.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                new_link = GroupTeam(group_id=group.id, team_id=team.id)
                session.add(new_link)
                links_created += 1
            else:
                links_skipped += 1
    
    await session.commit()
    print(f"✓ Group-Team links: {links_created} created, {links_skipped} skipped\n")
    return links_created


async def create_rounds(session):
    """Create all rounds in the database."""
    print("Creating rounds...")
    rounds_created = 0
    rounds_updated = 0
    
    # First, ensure ROUND_OF_32 exists in the database enum
    # This is a workaround for the migration that may not have been applied
    try:
        # Check if ROUND_OF_32 exists in the enum
        check_result = await session.execute(
            sa_text("SELECT 1 FROM pg_enum WHERE enumlabel = 'ROUND_OF_32' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'roundtype')")
        )
        exists = check_result.scalar_one_or_none()
        
        if not exists:
            # Try to add ROUND_OF_32 if it doesn't exist
            await session.execute(sa_text("ALTER TYPE roundtype ADD VALUE IF NOT EXISTS 'ROUND_OF_32'"))
            await session.commit()
            print("  Added ROUND_OF_32 to roundtype enum")
        else:
            print("  ROUND_OF_32 already exists in roundtype enum")
    except Exception as e:
        print(f"  Note: Could not check/add ROUND_OF_32 to enum: {e}")
        await session.rollback()
    
    for round_data in ROUNDS_DATA:
        result = await session.execute(
            select(Round).where(Round.name == round_data['name'])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update if needed
            updated = False
            # Compare using enum value
            if existing.round_type.value != round_data['type'].value:
                existing.round_type = round_data['type']
                updated = True
            if existing.order != round_data['order']:
                existing.order = round_data['order']
                updated = True
            if updated:
                rounds_updated += 1
                print(f"  Updated: {round_data['name']}")
        else:
            new_round = Round(
                name=round_data['name'],
                round_type=round_data['type'],
                order=round_data['order']
            )
            session.add(new_round)
            rounds_created += 1
            print(f"  Created: {round_data['name']} ({round_data['type'].value})")
    
    await session.commit()
    print(f"✓ Rounds: {rounds_created} created, {rounds_updated} updated\n")
    return rounds_created + rounds_updated


async def create_group_stage_games(session):
    """Create all group stage games."""
    print("Creating group stage games...")
    games_created = 0
    games_skipped = 0
    
    # Get all teams, groups, and rounds
    teams_result = await session.execute(select(Team))
    teams = {team.name: team for team in teams_result.scalars().all()}
    
    groups_result = await session.execute(select(Group))
    groups = {group.name: group for group in groups_result.scalars().all()}
    
    rounds_result = await session.execute(select(Round))
    rounds = {round.name: round for round in rounds_result.scalars().all()}
    
    match_number = 1
    
    for group_letter, home_team_name, away_team_name, match_date, matchday_name in GROUP_STAGE_MATCHES:
        group_name = f"Group {group_letter}"
        
        home_team = teams.get(home_team_name)
        away_team = teams.get(away_team_name)
        group = groups.get(group_name)
        round_obj = rounds.get(matchday_name)
        
        if not home_team:
            print(f"  WARNING: Home team {home_team_name} not found")
            continue
        if not away_team:
            print(f"  WARNING: Away team {away_team_name} not found")
            continue
        if not group:
            print(f"  WARNING: Group {group_name} not found")
            continue
        if not round_obj:
            print(f"  WARNING: Round {matchday_name} not found")
            continue
        
        # Create scheduled_at datetime (use 12:00 PM as default time)
        scheduled_at = datetime.combine(match_date, time(12, 0))
        
        # Check if game already exists
        result = await session.execute(
            select(Game).where(
                Game.home_team_id == home_team.id,
                Game.away_team_id == away_team.id,
                Game.match_date == match_date,
                Game.group_id == group.id
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            new_game = Game(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                scheduled_at=scheduled_at,
                match_date=match_date,
                status=GameStatus.SCHEDULED,
                round_id=round_obj.id,
                group_id=group.id,
                is_knockout=False,
                match_number=match_number
            )
            session.add(new_game)
            games_created += 1
            print(f"  Created: {home_team_name} vs {away_team_name} ({match_date}) - {matchday_name}")
            match_number += 1
        else:
            # Update existing game if needed
            updated = False
            if existing.match_date != match_date:
                existing.match_date = match_date
                updated = True
            if existing.scheduled_at != scheduled_at:
                existing.scheduled_at = scheduled_at
                updated = True
            if existing.round_id != round_obj.id:
                existing.round_id = round_obj.id
                updated = True
            if existing.group_id != group.id:
                existing.group_id = group.id
                updated = True
            if updated:
                games_skipped += 1  # Count as updated
                print(f"  Updated: {home_team_name} vs {away_team_name} ({match_date})")
            else:
                games_skipped += 1
    
    await session.commit()
    print(f"✓ Games: {games_created} created, {games_skipped} skipped/updated\n")
    return games_created


async def main():
    """Main function to populate database."""
    print("=" * 80)
    print("Populating 2026 FIFA World Cup Database")
    print("=" * 80)
    print()
    
    try:
        async with AsyncSessionLocal() as session:
            # Create teams
            await create_teams(session)
            
            # Create groups
            await create_groups(session)
            
            # Link teams to groups
            await link_teams_to_groups(session)
            
            # Create rounds
            await create_rounds(session)
            
            # Create group stage games
            await create_group_stage_games(session)
        
        print("=" * 80)
        print("✓ Database population complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

