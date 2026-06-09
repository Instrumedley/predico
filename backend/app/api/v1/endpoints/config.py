"""
Public configuration endpoints for the frontend.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class FeatureFlagsResponse(BaseModel):
    league_progress_chart: bool


@router.get("/features", response_model=FeatureFlagsResponse)
async def get_feature_flags() -> FeatureFlagsResponse:
    """Return feature flags consumed by the frontend."""
    return FeatureFlagsResponse(
        league_progress_chart=settings.LEAGUE_PROGRESS_CHART_ENABLED,
    )
