"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, games, standings, users, admin, predictions, leagues, config, knockout

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(standings.router, prefix="/standings", tags=["standings"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(knockout.router, prefix="/knockout", tags=["knockout"])

