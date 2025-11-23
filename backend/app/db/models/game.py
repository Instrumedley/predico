"""
Game/Match model for World Cup matches.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class GameStatus(str, enum.Enum):
    """Game status enumeration."""
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class Game(Base):
    """World Cup match/game model."""
    
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(SQLEnum(GameStatus), default=GameStatus.SCHEDULED, nullable=False, index=True)
    
    # Scores (null until game is finished)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    
    # Penalty shootout scores (if applicable)
    home_penalty_score = Column(Integer, nullable=True)
    away_penalty_score = Column(Integer, nullable=True)
    
    # Stadium and round information
    stadium_id = Column(Integer, ForeignKey("stadiums.id"), nullable=True, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)  # Only for group stage games
    
    # Additional information
    is_knockout = Column(Boolean, default=False, nullable=False, index=True)  # True for knockout rounds
    match_number = Column(Integer)  # Match number in the tournament
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Each game has exactly 2 teams: home_team and away_team
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    stadium = relationship("Stadium", back_populates="games")
    round = relationship("Round", back_populates="games")
    group = relationship("Group", back_populates="games")  # Only set for group stage games
    predictions = relationship("Prediction", back_populates="game", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Game(id={self.id}, {self.home_team_id} vs {self.away_team_id}, status={self.status.value})>"

