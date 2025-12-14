"""
User endpoints for getting current user information.
"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.db.models import User
from app.schemas.auth import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)

