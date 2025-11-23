"""
Prediction model for user game predictions.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Prediction(Base):
    """User prediction for a game."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    
    # Predicted scores
    predicted_home_score = Column(Integer, nullable=False)
    predicted_away_score = Column(Integer, nullable=False)
    
    # Points earned for this prediction (calculated after game is finished)
    points = Column(Integer, default=0, nullable=False, index=True)
    
    # Breakdown of points (for transparency)
    exact_score_points = Column(Integer, default=0)  # Points for exact score match
    correct_result_points = Column(Integer, default=0)  # Points for correct winner/draw
    correct_goal_difference_points = Column(Integer, default=0)  # Points for correct goal difference
    
    # Metadata
    is_calculated = Column(Boolean, default=False, nullable=False, index=True)  # Whether points have been calculated
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    game = relationship("Game", back_populates="predictions")
    
    # Unique constraint: one prediction per user per game
    __table_args__ = (
        Index("idx_user_game_unique", "user_id", "game_id", unique=True),
    )
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, user_id={self.user_id}, game_id={self.game_id}, points={self.points})>"

