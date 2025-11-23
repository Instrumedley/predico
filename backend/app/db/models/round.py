"""
Round/Phase model for tournament stages.
"""
from sqlalchemy import Column, String, Integer, Enum as SQLEnum
import enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class RoundType(str, enum.Enum):
    """Tournament round types."""
    GROUP_STAGE = "group_stage"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINALS = "quarter_finals"
    SEMI_FINALS = "semi_finals"
    THIRD_PLACE = "third_place"
    FINAL = "final"


class Round(Base):
    """Tournament round/phase model."""
    
    __tablename__ = "rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # e.g., "Group A", "Round of 16"
    round_type = Column(SQLEnum(RoundType), nullable=False, index=True)
    order = Column(Integer, nullable=False, index=True)  # Order in tournament (1=Group Stage, 2=Round of 16, etc.)
    
    # Relationships
    games = relationship("Game", back_populates="round")
    
    def __repr__(self):
        return f"<Round(id={self.id}, name={self.name}, round_type={self.round_type.value})>"

