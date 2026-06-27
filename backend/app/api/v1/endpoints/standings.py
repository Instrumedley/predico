"""
Standings endpoints for fetching group stage standings.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, or_
from sqlalchemy.orm import selectinload
from typing import List, Dict, Optional

from app.db.database import get_db
from app.db.models import Team, Group, GroupTeam, Game
from app.db.models.game import GameStatus
from app.services.knockout.standings_helpers import (
    get_knockout_qualified_team_ids,
    load_group_standings,
)
from pydantic import BaseModel

router = APIRouter()


class TeamStandingResponse(BaseModel):
    position: int
    country_code: str
    country_name: str
    flag_emoji: Optional[str] = None
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    qualified_to_knockout: bool = False

    class Config:
        from_attributes = True


class GroupStandingResponse(BaseModel):
    group_letter: str
    is_complete: bool = False
    teams: List[TeamStandingResponse]

    class Config:
        from_attributes = True


class StandingsResponse(BaseModel):
    groups: List[GroupStandingResponse]

    class Config:
        from_attributes = True


@router.get("", response_model=StandingsResponse)
async def get_standings(db: AsyncSession = Depends(get_db)):
    """
    Get group stage standings for all groups.
    
    Calculates standings based on completed games in the database.
    Teams with no games played will show 0 for all stats.
    """
    standings_by_group = await load_group_standings(db)
    qualified_team_ids = get_knockout_qualified_team_ids(standings_by_group)

    # Get all groups
    groups_query = select(Group).order_by(Group.name.asc())
    groups_result = await db.execute(groups_query)
    groups = groups_result.scalars().all()
    
    standings_groups = []
    
    for group in groups:
        # Get all teams in this group
        group_teams_query = select(GroupTeam).where(GroupTeam.group_id == group.id).options(
            selectinload(GroupTeam.team)
        )
        group_teams_result = await db.execute(group_teams_query)
        group_teams = group_teams_result.scalars().all()
        
        team_stats = []
        
        for group_team in group_teams:
            team = group_team.team
            
            # Get all games for this team in this group (as home or away)
            games_query = select(Game).where(
                Game.group_id == group.id,
                Game.status == GameStatus.FINISHED,
                or_(
                    Game.home_team_id == team.id,
                    Game.away_team_id == team.id
                )
            )
            games_result = await db.execute(games_query)
            games = games_result.scalars().all()
            
            # Calculate statistics
            played = len(games)
            wins = 0
            draws = 0
            losses = 0
            goals_for = 0
            goals_against = 0
            
            for game in games:
                is_home = game.home_team_id == team.id
                home_score = game.home_score or 0
                away_score = game.away_score or 0
                
                if is_home:
                    goals_for += home_score
                    goals_against += away_score
                    if home_score > away_score:
                        wins += 1
                    elif home_score == away_score:
                        draws += 1
                    else:
                        losses += 1
                else:
                    goals_for += away_score
                    goals_against += home_score
                    if away_score > home_score:
                        wins += 1
                    elif away_score == home_score:
                        draws += 1
                    else:
                        losses += 1
            
            goal_difference = goals_for - goals_against
            points = wins * 3 + draws
            
            team_stats.append({
                'team': team,
                'played': played,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goal_difference,
                'points': points
            })
        
        # Sort by points (desc), goal difference (desc), goals for (desc)
        team_stats.sort(key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for']))
        
        # Build team standings
        team_standings = []
        for position, stats in enumerate(team_stats, start=1):
            team = stats['team']
            team_standings.append(TeamStandingResponse(
                position=position,
                country_code=team.country_code,
                country_name=team.name,
                flag_emoji=team.flag_emoji,
                played=stats['played'],
                wins=stats['wins'],
                draws=stats['draws'],
                losses=stats['losses'],
                goals_for=stats['goals_for'],
                goals_against=stats['goals_against'],
                goal_difference=stats['goal_difference'],
                points=stats['points'],
                qualified_to_knockout=team.id in qualified_team_ids,
            ))
        
        # Extract group letter (e.g., "Group A" -> "A")
        group_letter = group.name.split()[-1] if ' ' in group.name else group.name
        group_meta = standings_by_group.get(group_letter.upper())
        is_complete = group_meta.is_complete if group_meta else False
        
        standings_groups.append(GroupStandingResponse(
            group_letter=group_letter,
            is_complete=is_complete,
            teams=team_standings
        ))
    
    return StandingsResponse(groups=standings_groups)


@router.get("/{group_letter}", response_model=GroupStandingResponse)
async def get_group_standings(group_letter: str, db: AsyncSession = Depends(get_db)):
    """
    Get standings for a specific group.
    """
    group_name = f"Group {group_letter.upper()}"
    standings_by_group = await load_group_standings(db)
    qualified_team_ids = get_knockout_qualified_team_ids(standings_by_group)
    
    # Get the group
    group_query = select(Group).where(Group.name == group_name)
    group_result = await db.execute(group_query)
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_letter} not found"
        )
    
    # Get all teams in this group
    group_teams_query = select(GroupTeam).where(GroupTeam.group_id == group.id).options(
        selectinload(GroupTeam.team)
    )
    group_teams_result = await db.execute(group_teams_query)
    group_teams = group_teams_result.scalars().all()
    
    team_stats = []
    
    for group_team in group_teams:
        team = group_team.team
        
        # Get all games for this team in this group (as home or away)
        games_query = select(Game).where(
            Game.group_id == group.id,
            Game.status == GameStatus.FINISHED,
            or_(
                Game.home_team_id == team.id,
                Game.away_team_id == team.id
            )
        )
        games_result = await db.execute(games_query)
        games = games_result.scalars().all()
        
        # Calculate statistics
        played = len(games)
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        
        for game in games:
            is_home = game.home_team_id == team.id
            home_score = game.home_score or 0
            away_score = game.away_score or 0
            
            if is_home:
                goals_for += home_score
                goals_against += away_score
                if home_score > away_score:
                    wins += 1
                elif home_score == away_score:
                    draws += 1
                else:
                    losses += 1
            else:
                goals_for += away_score
                goals_against += home_score
                if away_score > home_score:
                    wins += 1
                elif away_score == home_score:
                    draws += 1
                else:
                    losses += 1
        
        goal_difference = goals_for - goals_against
        points = wins * 3 + draws
        
        team_stats.append({
            'team': team,
            'played': played,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goal_difference,
            'points': points
        })
    
    # Sort by points (desc), goal difference (desc), goals for (desc)
    team_stats.sort(key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for']))
    
    # Build team standings
    team_standings = []
    for position, stats in enumerate(team_stats, start=1):
        team = stats['team']
        team_standings.append(TeamStandingResponse(
            position=position,
            country_code=team.country_code,
            country_name=team.name,
            flag_emoji=team.flag_emoji,
            played=stats['played'],
            wins=stats['wins'],
            draws=stats['draws'],
            losses=stats['losses'],
            goals_for=stats['goals_for'],
            goals_against=stats['goals_against'],
            goal_difference=stats['goal_difference'],
            points=stats['points'],
            qualified_to_knockout=team.id in qualified_team_ids,
        ))
    
    group_meta = standings_by_group.get(group_letter.upper())
    is_complete = group_meta.is_complete if group_meta else False

    return GroupStandingResponse(
        group_letter=group_letter.upper(),
        is_complete=is_complete,
        teams=team_standings
    )

