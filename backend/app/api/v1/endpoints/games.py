"""
Games endpoints for fetching match data.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import List, Optional

from app.db.database import get_db
from app.utils.match_time import get_game_kickoff_utc
from app.db.models import Game, Team, Round, Group, Stadium
from app.db.models.game import GameStatus
from pydantic import BaseModel

router = APIRouter()


class TeamResponse(BaseModel):
    id: int
    name: str
    country_code: str
    flag_emoji: Optional[str] = None

    class Config:
        from_attributes = True


class StadiumResponse(BaseModel):
    id: int
    name: str
    city: str

    class Config:
        from_attributes = True


class RoundResponse(BaseModel):
    id: int
    name: str
    round_type: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GameResponse(BaseModel):
    id: int
    home_team: TeamResponse
    away_team: TeamResponse
    scheduled_at: datetime
    match_date: Optional[date] = None
    match_time: Optional[str] = None  # Time as string (HH:MM:SS)
    timezone: Optional[str] = None  # Timezone string (e.g., "UTC-5")
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_penalty_score: Optional[int] = None
    away_penalty_score: Optional[int] = None
    stadium: Optional[StadiumResponse] = None
    round: RoundResponse
    group: Optional[GroupResponse] = None
    is_knockout: bool
    match_number: Optional[int] = None

    class Config:
        from_attributes = True


def game_to_response(game: Game) -> GameResponse:
    """Convert Game model to GameResponse, handling time serialization."""
    kickoff_utc = get_game_kickoff_utc(game) or game.scheduled_at
    return GameResponse(
        id=game.id,
        home_team=TeamResponse.model_validate(game.home_team),
        away_team=TeamResponse.model_validate(game.away_team),
        scheduled_at=kickoff_utc,
        match_date=game.match_date,
        match_time=game.match_time.strftime('%H:%M:%S') if game.match_time else None,
        timezone=game.timezone,
        status=game.status.value,
        home_score=game.home_score,
        away_score=game.away_score,
        home_penalty_score=game.home_penalty_score,
        away_penalty_score=game.away_penalty_score,
        stadium=StadiumResponse.model_validate(game.stadium) if game.stadium else None,
        round=RoundResponse.model_validate(game.round),
        group=GroupResponse.model_validate(game.group) if game.group else None,
        is_knockout=game.is_knockout,
        match_number=game.match_number,
    )


@router.get("", response_model=List[GameResponse])
async def get_games(
    status_filter: Optional[str] = Query(None, alias="status"),
    round_id: Optional[int] = Query(None),
    group_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of games with optional filters.
    """
    query = select(Game).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.stadium),
        selectinload(Game.round),
        selectinload(Game.group)
    )
    
    conditions = []
    
    if status_filter:
        try:
            status_enum = GameStatus(status_filter)
            conditions.append(Game.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}. Must be one of: scheduled, live, finished, cancelled, postponed"
            )
    
    if round_id:
        conditions.append(Game.round_id == round_id)
    
    if group_id:
        conditions.append(Game.group_id == group_id)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Game.scheduled_at.asc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    games = result.scalars().all()
    
    return [game_to_response(game) for game in games]


@router.get("/next", response_model=GameResponse)
async def get_next_game(db: AsyncSession = Depends(get_db)):
    """
    Get the next scheduled game based on match_date, match_time, and timezone.
    Falls back to scheduled_at if match_time/timezone are not available.
    """
    now = datetime.utcnow()
    
    # Get all scheduled games
    query = select(Game).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.stadium),
        selectinload(Game.round),
        selectinload(Game.group)
    ).where(
        Game.status == GameStatus.SCHEDULED
    )
    
    result = await db.execute(query)
    all_games = result.scalars().all()
    
    if not all_games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No upcoming games found"
        )
    
    # Find the next game by comparing UTC datetimes
    next_game = None
    next_datetime = None
    
    for game in all_games:
        match_utc = get_game_kickoff_utc(game)
        if match_utc and match_utc > now:
            if next_datetime is None or match_utc < next_datetime:
                next_datetime = match_utc
                next_game = game
    
    if not next_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No upcoming games found"
        )
    
    return game_to_response(next_game)


@router.get("/latest", response_model=List[GameResponse])
async def get_latest_games(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest finished games.
    """
    query = select(Game).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.stadium),
        selectinload(Game.round),
        selectinload(Game.group)
    ).where(
        Game.status == GameStatus.FINISHED
    ).order_by(Game.scheduled_at.desc()).limit(limit)
    
    result = await db.execute(query)
    games = result.scalars().all()
    
    return [game_to_response(game) for game in games]


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific game by ID.
    """
    query = select(Game).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.stadium),
        selectinload(Game.round),
        selectinload(Game.group)
    ).where(Game.id == game_id)
    
    result = await db.execute(query)
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {game_id} not found"
        )
    
    return game_to_response(game)

