"""Persisted admin results for knockout bracket matches."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class KnockoutMatchResult(Base):
    """Knockout match result used for bracket advancement (separate from 90-minute predictions)."""

    __tablename__ = "knockout_match_results"

    match_number = Column(Integer, primary_key=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    winner_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    winner_team = relationship("Team")

    def __repr__(self) -> str:
        return f"<KnockoutMatchResult(match_number={self.match_number}, winner_team_id={self.winner_team_id})>"
