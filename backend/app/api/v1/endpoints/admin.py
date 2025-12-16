"""
Admin endpoints for managing games and match results.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Game, User, Prediction
from app.db.models.game import GameStatus
from app.core.security import get_current_user

router = APIRouter()


class UpdateGameResultRequest(BaseModel):
    home_score: int
    away_score: int


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


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
    # This will be implemented when we add prediction scoring
    # For now, we'll create a placeholder structure
    await trigger_score_calculation_events(game, db)
    
    return {
        "message": "Game result updated successfully",
        "game_id": game.id,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "status": game.status.value
    }


async def trigger_score_calculation_events(game: Game, db: AsyncSession):
    """
    Trigger events for calculating prediction scores.
    
    This is a placeholder function that will be implemented when
    we add the prediction scoring system.
    
    Args:
        game: The game that was just finished
        db: Database session
    """
    # TODO: Implement prediction score calculation
    # This should:
    # 1. Get all predictions for this game
    # 2. Calculate points for each prediction based on:
    #    - Exact score match
    #    - Correct result (win/draw)
    #    - Correct goal difference
    # 3. Update user scores in leagues
    # 4. Update global user scores
    
    # Placeholder: Just log that we would calculate scores
    import structlog
    logger = structlog.get_logger(__name__)
    logger.info(
        "Score calculation event triggered",
        game_id=game.id,
        home_score=game.home_score,
        away_score=game.away_score
    )
    
    # For now, do nothing - this will be implemented later
    pass


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

