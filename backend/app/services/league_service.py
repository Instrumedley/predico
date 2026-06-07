"""
League helper functions for rankings, member points, and invitations.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LeagueInvitation, LeagueMember, Prediction, User
from app.services.token_service import TokenService

INVITE_EXPIRY_DAYS = 30


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


async def create_or_refresh_league_invitation(
    db: AsyncSession,
    league_id: int,
    inviter_id: int,
    invitee_email: str,
) -> str:
    """Create or refresh a pending invitation and return its accept token."""
    normalized_email = invitee_email.lower()
    token = TokenService.generate_token()
    expires_at = datetime.utcnow() + timedelta(days=INVITE_EXPIRY_DAYS)

    user_result = await db.execute(select(User).where(User.email == normalized_email))
    invitee = user_result.scalar_one_or_none()

    result = await db.execute(
        select(LeagueInvitation).where(
            LeagueInvitation.league_id == league_id,
            LeagueInvitation.invitee_email == normalized_email,
            LeagueInvitation.status == "pending",
        )
    )
    invitation = result.scalar_one_or_none()

    if invitation:
        invitation.token = token
        invitation.expires_at = expires_at
        invitation.inviter_id = inviter_id
        if invitee:
            invitation.invitee_id = invitee.id
    else:
        invitation = LeagueInvitation(
            league_id=league_id,
            inviter_id=inviter_id,
            invitee_id=invitee.id if invitee else None,
            invitee_email=normalized_email,
            token=token,
            status="pending",
            expires_at=expires_at,
        )
        db.add(invitation)

    await db.flush()
    return token


async def get_invitation_by_token(db: AsyncSession, token: str) -> Optional[LeagueInvitation]:
    """Return an invitation for the given token, regardless of status."""
    result = await db.execute(
        select(LeagueInvitation).where(LeagueInvitation.token == token)
    )
    return result.scalar_one_or_none()


async def accept_league_invitation(
    db: AsyncSession,
    invitation: LeagueInvitation,
    user: User,
) -> int:
    """Accept an invitation and add the user to the league. Returns league_id."""
    now = datetime.utcnow()
    if invitation.status != "pending":
        raise ValueError("Invitation is no longer valid")
    if invitation.expires_at and invitation.expires_at <= now:
        raise ValueError("Invitation has expired")
    if invitation.invitee_email.lower() != user.email.lower():
        raise ValueError("This invitation was sent to a different email address")

    existing = await db.execute(
        select(LeagueMember).where(
            LeagueMember.league_id == invitation.league_id,
            LeagueMember.user_id == user.id,
        )
    )
    if not existing.scalar_one_or_none():
        db.add(LeagueMember(league_id=invitation.league_id, user_id=user.id))

    invitation.status = "accepted"
    invitation.invitee_id = user.id
    invitation.responded_at = now
    return invitation.league_id


async def accept_pending_invites_for_user(db: AsyncSession, user: User) -> List[int]:
    """Accept all valid pending invitations sent to the user's email."""
    result = await db.execute(
        select(LeagueInvitation).where(
            LeagueInvitation.invitee_email == user.email.lower(),
            LeagueInvitation.status == "pending",
        )
    )
    joined: List[int] = []
    now = datetime.utcnow()

    for invitation in result.scalars().all():
        if invitation.expires_at and invitation.expires_at <= now:
            continue
        try:
            league_id = await accept_league_invitation(db, invitation, user)
            joined.append(league_id)
        except ValueError:
            continue

    if joined:
        await db.commit()

    return joined
