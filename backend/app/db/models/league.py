"""
League model for private prediction leagues.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class League(Base):
    """Private league for users to compete among themselves."""
    
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_private = Column(Boolean, default=True, nullable=False, index=True)
    invite_code = Column(String, unique=True, nullable=True, index=True)  # Unique code for joining
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_leagues")
    members = relationship("LeagueMember", back_populates="league", cascade="all, delete-orphan")
    invitations = relationship("LeagueInvitation", back_populates="league", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<League(id={self.id}, name={self.name}, created_by={self.created_by})>"


class LeagueMember(Base):
    """Association table for users in leagues (many-to-many with additional fields)."""
    
    __tablename__ = "league_members"
    
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # League-specific score (total points in this league)
    total_points = Column(Integer, default=0, nullable=False, index=True)
    
    # Metadata
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    league = relationship("League", back_populates="members")
    user = relationship("User", back_populates="league_memberships")
    
    # Unique constraint: one membership per user per league
    __table_args__ = (
        Index("idx_league_user_unique", "league_id", "user_id", unique=True),
    )
    
    def __repr__(self):
        return f"<LeagueMember(league_id={self.league_id}, user_id={self.user_id}, total_points={self.total_points})>"


class LeagueInvitation(Base):
    """League invitation model for tracking pending invitations."""
    
    __tablename__ = "league_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Status: pending, accepted, rejected, expired
    status = Column(String, default="pending", nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    league = relationship("League", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="sent_invitations")
    invitee = relationship("User", foreign_keys=[invitee_id], back_populates="received_invitations")
    
    def __repr__(self):
        return f"<LeagueInvitation(id={self.id}, league_id={self.league_id}, status={self.status})>"

