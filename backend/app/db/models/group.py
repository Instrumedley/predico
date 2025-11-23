"""
Group model for World Cup group stage.
"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Group(Base):
    """Group stage group model."""
    
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # e.g., "Group A", "Group B"
    
    # Relationships
    teams = relationship("GroupTeam", back_populates="group", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="group")
    
    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class GroupTeam(Base):
    """
    Association table for teams in groups (many-to-many).
    
    Note: These records are historical and remain in the database even after
    the group stage ends. They represent which teams were in which groups
    during the group stage phase. This is useful for:
    - Historical queries and statistics
    - Displaying group stage results
    - Understanding tournament progression
    
    When knockout rounds begin, teams advance based on group stage results,
    but the GroupTeam records are not deleted - they serve as a permanent
    record of the group stage composition.
    """
    
    __tablename__ = "group_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    
    # Relationships
    group = relationship("Group", back_populates="teams")
    team = relationship("Team", back_populates="group_memberships")
    
    def __repr__(self):
        return f"<GroupTeam(group_id={self.group_id}, team_id={self.team_id})>"

