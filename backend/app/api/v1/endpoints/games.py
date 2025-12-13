"""
Games endpoints for fetching match data.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import List, Optional

from app.db.database import get_db
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
    
    return games


@router.get("/next", response_model=GameResponse)
async def get_next_game(db: AsyncSession = Depends(get_db)):
    """
    Get the next scheduled game.
    """
    now = datetime.utcnow()
    
    query = select(Game).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.stadium),
        selectinload(Game.round),
        selectinload(Game.group)
    ).where(
        and_(
            Game.status == GameStatus.SCHEDULED,
            Game.scheduled_at >= now
        )
    ).order_by(Game.scheduled_at.asc()).limit(1)
    
    result = await db.execute(query)
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No upcoming games found"
        )
    
    return game


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
    
    return games


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
    
    return game

