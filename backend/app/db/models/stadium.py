"""
Stadium model for match venues.
"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class Stadium(Base):
    """Stadium/Venue model for World Cup matches."""
    
    __tablename__ = "stadiums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False)
    capacity = Column(Integer)  # Stadium capacity
    
    # Relationships
    games = relationship("Game", back_populates="stadium")
    
    def __repr__(self):
        return f"<Stadium(id={self.id}, name={self.name}, city={self.city})>"

