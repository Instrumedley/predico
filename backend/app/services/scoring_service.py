"""
Scoring service for calculating prediction points.

Scoring rules:
- 100 points for exact score match (both teams' goals correct)
- 50 points for correct outcome (win/draw)
- 15 points for correctly guessing how many goals a team scored (per team)
"""
from typing import Tuple
from app.db.models import Prediction, Game


def calculate_prediction_points(
    predicted_home_score: int,
    predicted_away_score: int,
    actual_home_score: int,
    actual_away_score: int,
) -> Tuple[int, dict]:
    """
    Calculate points for a prediction based on actual game result.
    
    Args:
        predicted_home_score: User's predicted home team score
        predicted_away_score: User's predicted away team score
        actual_home_score: Actual home team score
        actual_away_score: Actual away team score
    
    Returns:
        Tuple of (total_points, breakdown_dict) where breakdown contains:
        - exact_score_points: 100 if exact match, 0 otherwise
        - correct_result_points: 50 if correct outcome, 0 otherwise
        - correct_home_goals_points: 15 if home goals correct, 0 otherwise
        - correct_away_goals_points: 15 if away goals correct, 0 otherwise
    
    Examples:
        >>> calculate_prediction_points(2, 1, 2, 1)
        (100, {'exact_score_points': 100, 'correct_result_points': 0, 'correct_home_goals_points': 0, 'correct_away_goals_points': 0})
        
        >>> calculate_prediction_points(2, 0, 2, 1)
        (65, {'exact_score_points': 0, 'correct_result_points': 50, 'correct_home_goals_points': 15, 'correct_away_goals_points': 0})
        
        >>> calculate_prediction_points(3, 0, 2, 1)
        (50, {'exact_score_points': 0, 'correct_result_points': 50, 'correct_home_goals_points': 0, 'correct_away_goals_points': 0})
        
        >>> calculate_prediction_points(1, 1, 2, 1)
        (15, {'exact_score_points': 0, 'correct_result_points': 0, 'correct_home_goals_points': 0, 'correct_away_goals_points': 15})
        
        >>> calculate_prediction_points(1, 2, 2, 1)
        (0, {'exact_score_points': 0, 'correct_result_points': 0, 'correct_home_goals_points': 0, 'correct_away_goals_points': 0})
    """
    # Check for exact score match
    if predicted_home_score == actual_home_score and predicted_away_score == actual_away_score:
        return 100, {
            'exact_score_points': 100,
            'correct_result_points': 0,
            'correct_home_goals_points': 0,
            'correct_away_goals_points': 0,
        }
    
    # Calculate individual components
    breakdown = {
        'exact_score_points': 0,
        'correct_result_points': 0,
        'correct_home_goals_points': 0,
        'correct_away_goals_points': 0,
    }
    
    # Check correct outcome (win/draw)
    predicted_outcome = _get_outcome(predicted_home_score, predicted_away_score)
    actual_outcome = _get_outcome(actual_home_score, actual_away_score)
    
    if predicted_outcome == actual_outcome:
        breakdown['correct_result_points'] = 50
    
    # Check correct goals for each team
    if predicted_home_score == actual_home_score:
        breakdown['correct_home_goals_points'] = 15
    
    if predicted_away_score == actual_away_score:
        breakdown['correct_away_goals_points'] = 15
    
    total_points = sum(breakdown.values())
    
    return total_points, breakdown


def _get_outcome(home_score: int, away_score: int) -> str:
    """
    Determine the outcome of a match.
    
    Returns:
        'home_win', 'away_win', or 'draw'
    """
    if home_score > away_score:
        return 'home_win'
    elif away_score > home_score:
        return 'away_win'
    else:
        return 'draw'


def score_prediction(prediction: Prediction, game: Game) -> None:
    """
    Calculate and update points for a prediction based on game result.
    
    This function updates the prediction object in-place with calculated points.
    It should be called after a game has finished (status = FINISHED).
    
    Args:
        prediction: The Prediction object to score
        game: The Game object with actual results
    
    Raises:
        ValueError: If game is not finished or scores are missing
    """
    from app.db.models.game import GameStatus
    
    # Validate game is finished
    if game.status != GameStatus.FINISHED:
        raise ValueError(f"Game {game.id} is not finished. Cannot score predictions.")
    
    # Validate scores exist
    if game.home_score is None or game.away_score is None:
        raise ValueError(f"Game {game.id} scores are missing. Cannot score predictions.")
    
    # Calculate points
    total_points, breakdown = calculate_prediction_points(
        predicted_home_score=prediction.predicted_home_score,
        predicted_away_score=prediction.predicted_away_score,
        actual_home_score=game.home_score,
        actual_away_score=game.away_score,
    )
    
    # Update prediction with calculated points
    prediction.points = total_points
    prediction.exact_score_points = breakdown['exact_score_points']
    prediction.correct_result_points = breakdown['correct_result_points']
    # Store individual goal points in the goal_difference field for now
    # (we can add dedicated fields later if needed)
    prediction.correct_goal_difference_points = (
        breakdown['correct_home_goals_points'] + breakdown['correct_away_goals_points']
    )
    prediction.is_calculated = True


async def score_all_predictions_for_game(game: Game, db_session) -> int:
    """
    Score all predictions for a finished game.
    
    This function should be called after a game result is updated.
    It finds all predictions for the game and calculates points for each.
    
    Args:
        game: The Game object with actual results
        db_session: Database session
    
    Returns:
        Number of predictions scored
    
    Raises:
        ValueError: If game is not finished or scores are missing
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # Validate game is finished
    from app.db.models.game import GameStatus
    if game.status != GameStatus.FINISHED:
        raise ValueError(f"Game {game.id} is not finished. Cannot score predictions.")
    
    # Validate scores exist
    if game.home_score is None or game.away_score is None:
        raise ValueError(f"Game {game.id} scores are missing. Cannot score predictions.")
    
    # Get all predictions for this game
    query = select(Prediction).where(Prediction.game_id == game.id).options(
        selectinload(Prediction.user),
        selectinload(Prediction.game)
    )
    result = await db_session.execute(query)
    predictions = result.scalars().all()
    
    # Score each prediction
    scored_count = 0
    user_ids = set()
    for prediction in predictions:
        score_prediction(prediction, game)
        user_ids.add(prediction.user_id)
        scored_count += 1

    from app.services.league_service import sync_league_member_points

    for user_id in user_ids:
        await sync_league_member_points(db_session, user_id)

    # Commit all changes
    await db_session.commit()
    
    return scored_count

