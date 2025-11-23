"""
Database models module.
Import all models here so Alembic can detect them.
"""
from app.db.models.user import User
from app.db.models.team import Team
from app.db.models.stadium import Stadium
from app.db.models.round import Round, RoundType
from app.db.models.group import Group, GroupTeam
from app.db.models.game import Game, GameStatus
from app.db.models.prediction import Prediction
from app.db.models.league import League, LeagueMember, LeagueInvitation

__all__ = [
    "User",
    "Team",
    "Stadium",
    "Round",
    "RoundType",
    "Group",
    "GroupTeam",
    "Game",
    "GameStatus",
    "Prediction",
    "League",
    "LeagueMember",
    "LeagueInvitation",
]
