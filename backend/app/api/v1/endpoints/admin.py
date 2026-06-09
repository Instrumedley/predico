"""
Admin endpoints for managing games and match results.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Game, Prediction, User
from app.db.models.game import GameStatus
from app.api.v1.endpoints.games import GameResponse, game_to_response

router = APIRouter()


class UpdateGameResultRequest(BaseModel):
    home_score: int
    away_score: int


class AdminUserSummary(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    total_predictions: int
    total_points: int

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    users: List[AdminUserSummary]
    total: int


class AdminUserPredictionResponse(BaseModel):
    id: int
    predicted_home_score: int
    predicted_away_score: int
    points: int
    is_calculated: bool
    game: GameResponse


class AdminUserPredictionsResponse(BaseModel):
    user: AdminUserSummary
    predictions: List[AdminUserPredictionResponse]
    total_points: int


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    q: Optional[str] = Query(None, min_length=1, max_length=100),
    sort: str = Query("username"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Search and list users for the admin panel."""
    if sort not in {"username", "created_at"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort must be 'username' or 'created_at'",
        )

    total_points_expr = func.coalesce(func.sum(Prediction.points), 0).label("total_points")
    total_predictions_expr = func.count(Prediction.id).label("total_predictions")
    base_query = (
        select(User, total_points_expr, total_predictions_expr)
        .outerjoin(Prediction, Prediction.user_id == User.id)
        .group_by(User.id)
    )

    if q:
        search = f"%{q.strip()}%"
        base_query = base_query.where(
            or_(User.username.ilike(search), User.email.ilike(search))
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    order_by = (
        User.username.asc() if sort == "username" else User.created_at.desc()
    )
    query = base_query.order_by(order_by).limit(limit).offset(offset)
    result = await db.execute(query)

    users = [
        AdminUserSummary(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            total_predictions=int(total_predictions),
            total_points=int(total_points),
        )
        for user, total_points, total_predictions in result.all()
    ]

    return AdminUserListResponse(users=users, total=total)


@router.get("/users/{user_id}/predictions", response_model=AdminUserPredictionsResponse)
async def get_user_predictions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Return all predictions for a user with match context and scores."""
    user_query = (
        select(User, func.coalesce(func.sum(Prediction.points), 0).label("total_points"))
        .outerjoin(Prediction, Prediction.user_id == User.id)
        .where(User.id == user_id)
        .group_by(User.id)
    )
    user_result = await db.execute(user_query)
    user_row = user_result.first()

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    user, total_points = user_row

    predictions_query = (
        select(Prediction)
        .where(Prediction.user_id == user_id)
        .options(
            selectinload(Prediction.game).selectinload(Game.home_team),
            selectinload(Prediction.game).selectinload(Game.away_team),
            selectinload(Prediction.game).selectinload(Game.round),
            selectinload(Prediction.game).selectinload(Game.group),
            selectinload(Prediction.game).selectinload(Game.stadium),
        )
        .join(Game, Prediction.game_id == Game.id)
        .order_by(Game.match_date.asc(), Game.match_time.asc())
    )
    predictions_result = await db.execute(predictions_query)
    predictions = predictions_result.scalars().all()

    user_summary = AdminUserSummary(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        total_predictions=len(predictions),
        total_points=int(total_points),
    )

    return AdminUserPredictionsResponse(
        user=user_summary,
        total_points=int(total_points),
        predictions=[
            AdminUserPredictionResponse(
                id=prediction.id,
                predicted_home_score=prediction.predicted_home_score,
                predicted_away_score=prediction.predicted_away_score,
                points=prediction.points,
                is_calculated=prediction.is_calculated,
                game=game_to_response(prediction.game),
            )
            for prediction in predictions
        ],
    )


@router.put("/games/{game_id}/result", response_model=dict)
async def update_game_result(
    game_id: int,
    result: UpdateGameResultRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Update game result (scores) and mark game as finished.
    Only accessible by admin users.
    """
    # Get the game
    query = select(Game).where(Game.id == game_id).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.group),
        selectinload(Game.round)
    )
    result_query = await db.execute(query)
    game = result_query.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {game_id} not found"
        )
    
    # Update scores and status
    game.home_score = result.home_score
    game.away_score = result.away_score
    game.status = GameStatus.FINISHED
    
    await db.commit()
    await db.refresh(game)
    
    # TODO: Trigger events for score calculation
    from app.services.scoring_service import score_all_predictions_for_game

    scored = await score_all_predictions_for_game(game, db)
    
    return {
        "message": "Game result updated successfully",
        "game_id": game.id,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "status": game.status.value,
        "predictions_scored": scored,
    }


@router.post("/games/{game_id}/reset", response_model=dict)
async def reset_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Reset a game to its original state (no result, status = scheduled).
    This will:
    1. Reset game status to SCHEDULED (Upcoming)
    2. Clear game scores (set to None)
    3. Reset all predictions for this game (points = 0, is_calculated = False)
    4. Group standings will automatically recalculate when queried (only FINISHED games count)
    
    Only accessible by admin users.
    """
    # Get the game
    query = select(Game).where(Game.id == game_id).options(
        selectinload(Game.home_team),
        selectinload(Game.away_team),
        selectinload(Game.group),
        selectinload(Game.round)
    )
    result_query = await db.execute(query)
    game = result_query.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {game_id} not found"
        )
    
    # Reset game status and scores
    game.status = GameStatus.SCHEDULED
    game.home_score = None
    game.away_score = None
    game.home_penalty_score = None
    game.away_penalty_score = None
    
    # Get all predictions for this game and reset them
    predictions_query = select(Prediction).where(Prediction.game_id == game_id)
    predictions_result = await db.execute(predictions_query)
    predictions = predictions_result.scalars().all()
    
    for prediction in predictions:
        prediction.points = 0
        prediction.exact_score_points = 0
        prediction.correct_result_points = 0
        prediction.correct_goal_difference_points = 0
        prediction.is_calculated = False
    
    await db.commit()
    await db.refresh(game)
    
    return {
        "message": "Game reset successfully",
        "game_id": game.id,
        "status": game.status.value,
        "predictions_reset": len(predictions)
    }


@router.post("/games/reset-all", response_model=dict)
async def reset_all_games(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Reset all games to their original state (no results, status = scheduled).
    This will:
    1. Reset all game statuses to SCHEDULED (Upcoming)
    2. Clear all game scores (set to None)
    3. Reset all predictions (points = 0, is_calculated = False)
    4. Group standings will automatically recalculate when queried (only FINISHED games count)
    
    This brings the system back to the initial state.
    Only accessible by admin users.
    """
    # Get all games
    games_query = select(Game)
    games_result = await db.execute(games_query)
    games = games_result.scalars().all()
    
    games_reset = 0
    
    # Reset all games
    for game in games:
        game.status = GameStatus.SCHEDULED
        game.home_score = None
        game.away_score = None
        game.home_penalty_score = None
        game.away_penalty_score = None
        games_reset += 1
    
    # Get all predictions and reset them
    predictions_query = select(Prediction)
    predictions_result = await db.execute(predictions_query)
    predictions = predictions_result.scalars().all()
    
    predictions_reset = 0
    for prediction in predictions:
        prediction.points = 0
        prediction.exact_score_points = 0
        prediction.correct_result_points = 0
        prediction.correct_goal_difference_points = 0
        prediction.is_calculated = False
        predictions_reset += 1
    
    await db.commit()
    
    return {
        "message": "All games reset successfully",
        "games_reset": games_reset,
        "predictions_reset": predictions_reset
    }

