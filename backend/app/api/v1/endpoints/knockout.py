"""Knockout bracket endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.knockout.bracket_service import bracket_to_api_dict, build_knockout_bracket

router = APIRouter()


@router.get("/bracket")
async def get_knockout_bracket(db: AsyncSession = Depends(get_db)):
    """Return the computed knockout bracket from standings and admin results."""
    bracket = await build_knockout_bracket(db)
    return bracket_to_api_dict(bracket)
