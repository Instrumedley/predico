"""
Public configuration endpoints for the frontend.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class FeatureFlagsResponse(BaseModel):
    league_progress_chart: bool
    knockout_stage: bool
    knockout_stage_default: bool


@router.get("/features", response_model=FeatureFlagsResponse)
async def get_feature_flags() -> FeatureFlagsResponse:
    """Return feature flags consumed by the frontend."""
    return FeatureFlagsResponse(
        league_progress_chart=settings.LEAGUE_PROGRESS_CHART_ENABLED,
        knockout_stage=settings.KNOCKOUT_STAGE_ENABLED,
        knockout_stage_default=settings.KNOCKOUT_STAGE_DEFAULT,
    )
