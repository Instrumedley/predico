"""
User model for authentication and user information.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    """User model for authentication and profile information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False, nullable=False, index=True)
    email_verification_token = Column(String, nullable=True, unique=True, index=True)
    password_reset_token = Column(String, nullable=True, unique=True, index=True)
    password_reset_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    created_leagues = relationship("League", back_populates="creator", foreign_keys="League.created_by")
    league_memberships = relationship("LeagueMember", back_populates="user", cascade="all, delete-orphan")
    sent_invitations = relationship("LeagueInvitation", back_populates="inviter", foreign_keys="LeagueInvitation.inviter_id")
    received_invitations = relationship("LeagueInvitation", back_populates="invitee", foreign_keys="LeagueInvitation.invitee_id")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

