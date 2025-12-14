"""
Unit tests for prediction scoring logic.
"""
import pytest
from app.services.scoring_service import calculate_prediction_points, score_prediction
from app.db.models import Prediction, Game
from app.db.models.game import GameStatus


class TestCalculatePredictionPoints:
    """Test cases for calculate_prediction_points function."""
    
    def test_exact_score_match(self):
        """User 1: Exact score match should get 100 points."""
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 2, Team B 1
        points, breakdown = calculate_prediction_points(2, 1, 2, 1)
        
        assert points == 100
        assert breakdown['exact_score_points'] == 100
        assert breakdown['correct_result_points'] == 0
        assert breakdown['correct_home_goals_points'] == 0
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_correct_outcome_and_home_goals(self):
        """User 2: Correct outcome + correct home goals should get 65 points."""
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 2, Team B 0
        points, breakdown = calculate_prediction_points(2, 0, 2, 1)
        
        assert points == 65
        assert breakdown['exact_score_points'] == 0
        assert breakdown['correct_result_points'] == 50  # Correct outcome (A wins)
        assert breakdown['correct_home_goals_points'] == 15  # Correct home goals
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_correct_outcome_only(self):
        """User 3: Correct outcome only should get 50 points."""
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 3, Team B 0
        points, breakdown = calculate_prediction_points(3, 0, 2, 1)
        
        assert points == 50
        assert breakdown['exact_score_points'] == 0
        assert breakdown['correct_result_points'] == 50  # Correct outcome (A wins)
        assert breakdown['correct_home_goals_points'] == 0
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_correct_away_goals_only(self):
        """User 4: Correct away goals only should get 15 points."""
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 1, Team B 1 (draw prediction)
        points, breakdown = calculate_prediction_points(1, 1, 2, 1)
        
        assert points == 15
        assert breakdown['exact_score_points'] == 0
        assert breakdown['correct_result_points'] == 0  # Wrong outcome (predicted draw, actual A wins)
        assert breakdown['correct_home_goals_points'] == 0
        assert breakdown['correct_away_goals_points'] == 15  # Correct away goals
    
    def test_zero_points(self):
        """User 5: Wrong outcome and wrong goals should get 0 points."""
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 1, Team B 2
        points, breakdown = calculate_prediction_points(1, 2, 2, 1)
        
        assert points == 0
        assert breakdown['exact_score_points'] == 0
        assert breakdown['correct_result_points'] == 0  # Wrong outcome (predicted B wins, actual A wins)
        assert breakdown['correct_home_goals_points'] == 0
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_correct_draw_outcome(self):
        """Test correct draw prediction."""
        # Actual: Team A 1, Team B 1 (draw)
        # Prediction: Team A 0, Team B 0 (draw)
        points, breakdown = calculate_prediction_points(0, 0, 1, 1)
        
        assert points == 50
        assert breakdown['exact_score_points'] == 0
        assert breakdown['correct_result_points'] == 50  # Correct outcome (draw)
        assert breakdown['correct_home_goals_points'] == 0
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_correct_away_win_outcome(self):
        """Test correct away win prediction."""
        # Actual: Team A 0, Team B 2 (B wins)
        # Prediction: Team A 1, Team B 3 (B wins)
        points, breakdown = calculate_prediction_points(1, 3, 0, 2)
        
        assert points == 50
        assert breakdown['exact_score_points'] == 0
        assert breakdown['correct_result_points'] == 50  # Correct outcome (B wins)
        assert breakdown['correct_home_goals_points'] == 0
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_both_goals_correct_but_wrong_outcome(self):
        """Test both goals correct but wrong outcome (shouldn't happen but test edge case)."""
        # This scenario shouldn't occur in practice, but test for robustness
        # Actual: Team A 2, Team B 2 (draw)
        # Prediction: Team A 2, Team B 2 (draw) - but this would be exact match
        # Let's test: Actual draw, but prediction has same scores but different outcome logic
        # Actually, if both scores match, it's always exact match, so let's test a different case
        # Actual: Team A 1, Team B 1 (draw)
        # Prediction: Team A 1, Team B 1 (draw) - exact match
        points, breakdown = calculate_prediction_points(1, 1, 1, 1)
        
        assert points == 100  # Exact match
        assert breakdown['exact_score_points'] == 100
    
    def test_correct_home_goals_only(self):
        """Test correct home goals only."""
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 2, Team B 0
        points, breakdown = calculate_prediction_points(2, 0, 2, 1)
        
        assert points == 65  # 50 for outcome + 15 for home goals
        assert breakdown['correct_result_points'] == 50
        assert breakdown['correct_home_goals_points'] == 15
        assert breakdown['correct_away_goals_points'] == 0
    
    def test_correct_both_goals_but_wrong_outcome(self):
        """Test both goals correct but wrong outcome (edge case)."""
        # This is mathematically impossible, but test for code robustness
        # If both goals are correct, outcome must be correct too
        # So this test verifies the logic handles it correctly
        # Actual: Team A 2, Team B 1
        # Prediction: Team A 2, Team B 1
        # This is exact match, so should return 100
        points, breakdown = calculate_prediction_points(2, 1, 2, 1)
        
        assert points == 100
        assert breakdown['exact_score_points'] == 100


class TestScorePrediction:
    """Test cases for score_prediction function."""
    
    @pytest.mark.asyncio
    async def test_score_prediction_success(self, db_session):
        """Test scoring a prediction successfully."""
        from datetime import datetime
        from app.db.models import Team, Round, RoundType, User
        
        # Create test data
        home_team = Team(name="Team A", country_code="TEA")
        away_team = Team(name="Team B", country_code="TEB")
        round_obj = Round(name="Test Round", round_type=RoundType.GROUP_STAGE, order=1)
        
        db_session.add_all([home_team, away_team, round_obj])
        await db_session.commit()
        
        # Create a finished game
        game = Game(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            scheduled_at=datetime(2026, 6, 15, 12, 0, 0),
            status=GameStatus.FINISHED,
            home_score=2,
            away_score=1,
            round_id=round_obj.id,
        )
        db_session.add(game)
        await db_session.commit()
        
        # Create a prediction
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        
        prediction = Prediction(
            user_id=user.id,
            game_id=game.id,
            predicted_home_score=2,
            predicted_away_score=1,
        )
        db_session.add(prediction)
        await db_session.commit()
        
        # Score the prediction
        score_prediction(prediction, game)
        await db_session.commit()
        
        # Verify points
        assert prediction.points == 100
        assert prediction.exact_score_points == 100
        assert prediction.correct_result_points == 0
        assert prediction.is_calculated is True
    
    @pytest.mark.asyncio
    async def test_score_prediction_not_finished(self, db_session):
        """Test that scoring fails if game is not finished."""
        from datetime import datetime
        from app.db.models import Team, Round, RoundType, User
        
        home_team = Team(name="Team A", country_code="TEA")
        away_team = Team(name="Team B", country_code="TEB")
        round_obj = Round(name="Test Round", round_type=RoundType.GROUP_STAGE, order=1)
        
        db_session.add_all([home_team, away_team, round_obj])
        await db_session.commit()
        
        game = Game(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            scheduled_at=datetime(2026, 6, 15, 12, 0, 0),
            status=GameStatus.SCHEDULED,  # Not finished
            home_score=None,
            away_score=None,
            round_id=round_obj.id,
        )
        db_session.add(game)
        await db_session.commit()
        
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        
        prediction = Prediction(
            user_id=user.id,
            game_id=game.id,
            predicted_home_score=2,
            predicted_away_score=1,
        )
        db_session.add(prediction)
        await db_session.commit()
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="is not finished"):
            score_prediction(prediction, game)
    
    @pytest.mark.asyncio
    async def test_score_prediction_missing_scores(self, db_session):
        """Test that scoring fails if game scores are missing."""
        from datetime import datetime
        from app.db.models import Team, Round, RoundType, User
        
        home_team = Team(name="Team A", country_code="TEA")
        away_team = Team(name="Team B", country_code="TEB")
        round_obj = Round(name="Test Round", round_type=RoundType.GROUP_STAGE, order=1)
        
        db_session.add_all([home_team, away_team, round_obj])
        await db_session.commit()
        
        game = Game(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            scheduled_at=datetime(2026, 6, 15, 12, 0, 0),
            status=GameStatus.FINISHED,
            home_score=None,  # Missing score
            away_score=1,
            round_id=round_obj.id,
        )
        db_session.add(game)
        await db_session.commit()
        
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        
        prediction = Prediction(
            user_id=user.id,
            game_id=game.id,
            predicted_home_score=2,
            predicted_away_score=1,
        )
        db_session.add(prediction)
        await db_session.commit()
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="scores are missing"):
            score_prediction(prediction, game)

