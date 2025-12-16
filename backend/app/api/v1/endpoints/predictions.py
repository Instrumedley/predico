"""
Predictions endpoints for user game predictions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Prediction, Game, User
from app.core.security import get_current_user

router = APIRouter()


class PredictionCreate(BaseModel):
    game_id: int
    predicted_home_score: int
    predicted_away_score: int


class PredictionResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    predicted_home_score: int
    predicted_away_score: int
    points: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchPredictionCreate(BaseModel):
    predictions: List[PredictionCreate]


@router.get("", response_model=List[PredictionResponse])
async def get_user_predictions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all predictions for the current user.
    """
    query = select(Prediction).where(Prediction.user_id == current_user.id)
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return predictions


@router.get("/game/{game_id}", response_model=PredictionResponse)
async def get_prediction_for_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get prediction for a specific game for the current user.
    """
    query = select(Prediction).where(
        Prediction.user_id == current_user.id,
        Prediction.game_id == game_id
    )
    result = await db.execute(query)
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found for this game"
        )
    
    return prediction


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_prediction(
    prediction_data: PredictionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update a prediction for a game.
    If a prediction already exists for this user and game, it will be updated.
    """
    # Validate that the game exists
    game_query = select(Game).where(Game.id == prediction_data.game_id)
    game_result = await db.execute(game_query)
    game = game_result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {prediction_data.game_id} not found"
        )
    
    # Check if prediction already exists
    existing_query = select(Prediction).where(
        Prediction.user_id == current_user.id,
        Prediction.game_id == prediction_data.game_id
    )
    existing_result = await db.execute(existing_query)
    existing_prediction = existing_result.scalar_one_or_none()
    
    if existing_prediction:
        # Update existing prediction
        existing_prediction.predicted_home_score = prediction_data.predicted_home_score
        existing_prediction.predicted_away_score = prediction_data.predicted_away_score
        # Reset points if game hasn't been scored yet
        if not existing_prediction.is_calculated:
            existing_prediction.points = 0
        await db.commit()
        await db.refresh(existing_prediction)
        return existing_prediction
    else:
        # Create new prediction
        new_prediction = Prediction(
            user_id=current_user.id,
            game_id=prediction_data.game_id,
            predicted_home_score=prediction_data.predicted_home_score,
            predicted_away_score=prediction_data.predicted_away_score,
            points=0
        )
        db.add(new_prediction)
        await db.commit()
        await db.refresh(new_prediction)
        return new_prediction


@router.post("/batch", response_model=List[PredictionResponse], status_code=status.HTTP_201_CREATED)
async def create_or_update_predictions_batch(
    batch_data: BatchPredictionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update multiple predictions in a single request.
    If a prediction already exists for a user and game, it will be updated.
    """
    if not batch_data.predictions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No predictions provided"
        )
    
    # Validate all games exist
    game_ids = {p.game_id for p in batch_data.predictions}
    games_query = select(Game).where(Game.id.in_(game_ids))
    games_result = await db.execute(games_query)
    existing_games = {game.id for game in games_result.scalars().all()}
    
    missing_games = game_ids - existing_games
    if missing_games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Games not found: {missing_games}"
        )
    
    # Get all existing predictions for this user and these games
    existing_query = select(Prediction).where(
        Prediction.user_id == current_user.id,
        Prediction.game_id.in_(game_ids)
    )
    existing_result = await db.execute(existing_query)
    existing_predictions = {
        pred.game_id: pred for pred in existing_result.scalars().all()
    }
    
    results = []
    
    for pred_data in batch_data.predictions:
        if pred_data.game_id in existing_predictions:
            # Update existing prediction
            existing_pred = existing_predictions[pred_data.game_id]
            existing_pred.predicted_home_score = pred_data.predicted_home_score
            existing_pred.predicted_away_score = pred_data.predicted_away_score
            # Reset points if game hasn't been scored yet
            if not existing_pred.is_calculated:
                existing_pred.points = 0
            results.append(existing_pred)
        else:
            # Create new prediction
            new_prediction = Prediction(
                user_id=current_user.id,
                game_id=pred_data.game_id,
                predicted_home_score=pred_data.predicted_home_score,
                predicted_away_score=pred_data.predicted_away_score,
                points=0
            )
            db.add(new_prediction)
            results.append(new_prediction)
    
    await db.commit()
    
    # Refresh all predictions to get updated timestamps
    for pred in results:
        await db.refresh(pred)
    
    return results

