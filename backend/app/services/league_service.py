"""
League helper functions for rankings and member points.
"""
from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LeagueMember, Prediction, User


async def get_league_rankings(db: AsyncSession, league_id: int) -> List[Tuple[int, str, int]]:
    """
    Return league standings as (user_id, username, total_points) sorted by points desc.
    Points are the sum of all scored predictions for each member.
    """
    points_subquery = (
        select(
            Prediction.user_id.label("user_id"),
            func.coalesce(func.sum(Prediction.points), 0).label("total_points"),
        )
        .group_by(Prediction.user_id)
        .subquery()
    )

    result = await db.execute(
        select(
            User.id,
            User.username,
            func.coalesce(points_subquery.c.total_points, 0).label("total_points"),
        )
        .join(LeagueMember, LeagueMember.user_id == User.id)
        .outerjoin(points_subquery, points_subquery.c.user_id == User.id)
        .where(LeagueMember.league_id == league_id)
        .order_by(func.coalesce(points_subquery.c.total_points, 0).desc(), User.username.asc())
    )

    return [(row.id, row.username, int(row.total_points)) for row in result.all()]


async def sync_league_member_points(db: AsyncSession, user_id: int) -> None:
    """Update cached total_points on all league memberships for a user."""
    points_result = await db.execute(
        select(func.coalesce(func.sum(Prediction.points), 0)).where(Prediction.user_id == user_id)
    )
    total_points = int(points_result.scalar_one())

    members_result = await db.execute(select(LeagueMember).where(LeagueMember.user_id == user_id))
    for member in members_result.scalars().all():
        member.total_points = total_points
