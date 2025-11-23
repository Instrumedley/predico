"""
Team model for national teams.
"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class Team(Base):
    """National team model."""
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    country_code = Column(String(3), unique=True, nullable=False, index=True)  # ISO 3166-1 alpha-3
    flag_emoji = Column(String(10))  # Flag emoji for display
    fifa_ranking = Column(Integer)  # Current FIFA ranking (optional)
    
    # Relationships
    # A team can be home_team or away_team in multiple games
    # Each game has exactly 2 teams: one home_team and one away_team
    home_games = relationship("Game", back_populates="home_team", foreign_keys="Game.home_team_id")
    away_games = relationship("Game", back_populates="away_team", foreign_keys="Game.away_team_id")
    # A team belongs to a group during group stage (historical record after group stage ends)
    group_memberships = relationship("GroupTeam", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, country_code={self.country_code})>"
    
    # Note: To get all games for a team, query both home_games and away_games
    # Example: team.home_games + team.away_games (or use SQLAlchemy OR with or_())

