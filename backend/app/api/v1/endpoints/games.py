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
from app.utils.match_time import get_game_kickoff_utc, get_prediction_deadline_utc, are_teams_resolved
from app.db.models import Game, Team, Round, Group, Stadium
from app.db.models.game import GameStatus
from app.services.knockout.bracket_service import ResolvedMatch, resolve_all_knockout_matches
from app.services.knockout.knockout_sync_service import resolved_match_to_slot_labels
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
    home_team: Optional[TeamResponse] = None
    away_team: Optional[TeamResponse] = None
    home_slot_label: Optional[str] = None
    away_slot_label: Optional[str] = None
    teams_resolved: bool
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


def game_to_response(
    game: Game,
    resolved: ResolvedMatch | None = None,
) -> GameResponse:
    """Convert Game model to GameResponse, handling nullable teams and slot labels."""
    kickoff_utc = get_game_kickoff_utc(game) or game.scheduled_at
    home_slot_label, away_slot_label = resolved_match_to_slot_labels(resolved)

    return GameResponse(
        id=game.id,
        home_team=TeamResponse.model_validate(game.home_team) if game.home_team else None,
        away_team=TeamResponse.model_validate(game.away_team) if game.away_team else None,
        home_slot_label=home_slot_label,
        away_slot_label=away_slot_label,
        teams_resolved=are_teams_resolved(game),
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


async def _build_game_responses(games: list[Game], db: AsyncSession) -> list[GameResponse]:
    has_knockout = any(game.is_knockout for game in games)
    resolved_map: dict[int, ResolvedMatch] = {}
    if has_knockout:
        resolved_map = await resolve_all_knockout_matches(db)

    return [
        game_to_response(game, resolved_map.get(game.match_number) if game.match_number else None)
        for game in games
    ]


def _is_predictable_game(game: Game) -> bool:
    return game.status == GameStatus.SCHEDULED and are_teams_resolved(game)


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
    
    query = query.order_by(Game.match_date.asc(), Game.match_time.asc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    games = result.scalars().all()
    
    return await _build_game_responses(games, db)


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
        if not _is_predictable_game(game):
            continue
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
    
    return (await _build_game_responses([next_game], db))[0]


@router.get("/next-deadline", response_model=GameResponse)
async def get_next_deadline_game(db: AsyncSession = Depends(get_db)):
    """
    Get the scheduled game whose prediction deadline (1 hour before kickoff) is
    the soonest among deadlines still in the future.
    """
    now = datetime.utcnow()

    query = select(Game).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.stadium),
        selectinload(Game.round),
        selectinload(Game.group),
    ).where(Game.status == GameStatus.SCHEDULED)

    result = await db.execute(query)
    all_games = result.scalars().all()

    next_game = None
    next_deadline = None

    for game in all_games:
        if not _is_predictable_game(game):
            continue
        deadline = get_prediction_deadline_utc(game)
        if deadline and deadline > now:
            if next_deadline is None or deadline < next_deadline:
                next_deadline = deadline
                next_game = game

    if not next_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No upcoming prediction deadlines found",
        )

    return (await _build_game_responses([next_game], db))[0]


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
    ).order_by(Game.match_date.desc(), Game.match_time.desc()).limit(limit)
    
    result = await db.execute(query)
    games = result.scalars().all()
    
    return await _build_game_responses(games, db)


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
    
    return (await _build_game_responses([game], db))[0]

