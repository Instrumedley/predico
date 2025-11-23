"""
Token service for generating and validating verification/reset tokens.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User
import structlog

logger = structlog.get_logger()


class TokenService:
    """Service for managing verification and reset tokens."""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def create_verification_token(user_id: int, db: AsyncSession) -> str:
        """
        Create and store email verification token for user.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Verification token
        """
        token = TokenService.generate_token()
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.email_verification_token = token
            await db.commit()
            logger.info("Verification token created", user_id=user_id)
        
        return token
    
    @staticmethod
    async def verify_email_token(token: str, db: AsyncSession) -> Optional[User]:
        """
        Verify email verification token and mark email as verified.
        
        Args:
            token: Verification token
            db: Database session
            
        Returns:
            User if token is valid, None otherwise
        """
        result = await db.execute(
            select(User).where(User.email_verification_token == token)
        )
        user = result.scalar_one_or_none()
        
        if user:
            if user.email_verified:
                logger.warning("Email already verified", user_id=user.id)
                return user  # Idempotent - return user even if already verified
            
            user.email_verified = True
            user.email_verification_token = None  # Clear token after use
            await db.commit()
            logger.info("Email verified", user_id=user.id)
            return user
        
        logger.warning("Invalid verification token", token=token[:10])
        return None
    
    @staticmethod
    async def create_password_reset_token(user_id: int, db: AsyncSession) -> str:
        """
        Create and store password reset token for user.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Password reset token
        """
        token = TokenService.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.password_reset_token = token
            user.password_reset_expires = expires_at
            await db.commit()
            logger.info("Password reset token created", user_id=user_id)
        
        return token
    
    @staticmethod
    async def verify_password_reset_token(token: str, db: AsyncSession) -> Optional[User]:
        """
        Verify password reset token.
        
        Args:
            token: Password reset token
            db: Database session
            
        Returns:
            User if token is valid and not expired, None otherwise
        """
        result = await db.execute(
            select(User).where(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.info("Password reset token verified", user_id=user.id)
            return user
        
        logger.warning("Invalid or expired password reset token", token=token[:10])
        return None
    
    @staticmethod
    async def clear_password_reset_token(user_id: int, db: AsyncSession) -> None:
        """
        Clear password reset token after successful reset.
        
        Args:
            user_id: User ID
            db: Database session
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.password_reset_token = None
            user.password_reset_expires = None
            await db.commit()
            logger.info("Password reset token cleared", user_id=user_id)

