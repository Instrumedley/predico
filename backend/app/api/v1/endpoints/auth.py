"""
Authentication endpoints for signup, login, email verification, and password reset.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    SignupResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.services.email_service import email_service
from app.services.league_service import accept_pending_invites_for_user
from app.services.token_service import TokenService
from app.services.cognito_service import cognito_service
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    
    Creates a new user account and sends verification email.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user in Cognito if enabled
    cognito_user_id = None
    if settings.COGNITO_ENABLED:
        try:
            cognito_result = await cognito_service.sign_up(
                email=user_data.email,
                password=user_data.password,
                username=user_data.username,
            )
            cognito_user_id = cognito_result.get("sub")
            # If Cognito handles email verification, user is already confirmed
            email_verified = cognito_result.get("user_confirmed", False)
        except ValueError as e:
            # Cognito validation error (e.g., password policy, duplicate email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    else:
        email_verified = False
    
    # Create user in our database
    # We still store password hash for local auth fallback and consistency
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        email_verified=email_verified,
        cognito_user_id=cognito_user_id,  # Store Cognito user ID if available
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate verification token and send email (if not using Cognito email verification)
    if not settings.COGNITO_ENABLED or not email_verified:
        # Create token directly on the user object to ensure it's saved
        verification_token = TokenService.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        new_user.email_verification_token = verification_token
        new_user.email_verification_expires = expires_at
        await db.commit()
        await email_service.send_verification_email(new_user.email, verification_token, username=new_user.username)
    
    return SignupResponse(
        user=UserResponse.model_validate(new_user),
        message="User created successfully. Please check your email to verify your account."
    )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    If Cognito is enabled, authenticates with Cognito first, then looks up user in database.
    If Cognito is disabled, uses local password verification.
    """
    # Authenticate with Cognito if enabled
    if settings.COGNITO_ENABLED:
        try:
            # Authenticate with Cognito
            cognito_tokens = await cognito_service.authenticate(
                email=credentials.email,
                password=credentials.password,
            )
            
            # Find user in database by email or cognito_user_id
            # Note: We could also decode the Cognito ID token to get the sub
            result = await db.execute(select(User).where(User.email == credentials.email))
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found in database"
                )
        except ValueError as e:
            # Cognito authentication failed
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    else:
        # Local authentication
        result = await db.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token (our JWT for API authentication)
    if credentials.remember_me:
        expires_delta = timedelta(days=settings.REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    else:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=expires_delta,
    )

    await accept_pending_invites_for_user(db, user)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email with verification token.
    """
    user = await TokenService.verify_email_token(request.token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    await accept_pending_invites_for_user(db, user)
    
    return VerifyEmailResponse(
        message="Email verified successfully"
    )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend email verification link.
    
    Only sends email if:
    - User exists in database
    - User's email is not already verified
    
    Returns the same message regardless to prevent email enumeration attacks.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # Only send email if user exists AND email is not verified
    # This prevents:
    # 1. Spamming non-existent emails
    # 2. Spamming already-verified users
    if user:
        if user.email_verified:
            # Email already verified - don't send, but return success message
            # to prevent revealing that the email exists and is verified
            logger.info("Resend verification requested for already verified email", email=request.email)
        else:
            # User exists and email not verified - send verification email
            verification_token = await TokenService.create_verification_token(user.id, db)
            await email_service.send_verification_email(user.email, verification_token, username=user.username)
            logger.info("Verification email resent", email=request.email, user_id=user.id)
    else:
        # User doesn't exist - don't send email, but return success message
        # to prevent email enumeration attacks
        logger.warning("Resend verification requested for non-existent email", email=request.email)
    
    # Always return the same message to prevent email enumeration
    return ResendVerificationResponse(
        message="If the email exists and is not verified, a verification link has been sent."
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset email.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # For security, always return success even if user doesn't exist
    if user:
        reset_token = await TokenService.create_password_reset_token(user.id, db)
        await email_service.send_password_reset_email(user.email, reset_token, username=user.username)
    
    return ForgotPasswordResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using reset token.
    """
    # Verify token
    user = await TokenService.verify_password_reset_token(request.token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    await TokenService.clear_password_reset_token(user.id, db)
    await db.commit()
    
    return ResetPasswordResponse(
        message="Password reset successfully"
    )

