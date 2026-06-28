"""
League helper functions for rankings, member points, and invitations.
"""
from datetime import datetime, time, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import League, LeagueInvitation, LeagueMember, Prediction, User
from app.services.token_service import TokenService

INVITE_EXPIRY_DAYS = 30

LeagueRankingRow = Tuple[int, str, int, int]


def assign_league_ranks(rows: List[LeagueRankingRow]) -> List[Tuple[int, int, str, int, int]]:
    """
    Assign ranks to pre-sorted league rows.

    Rows must be ordered by total_points desc, perfect_predictions desc, username asc.
    Players with the same points and perfect predictions share a rank.
    """
    ranked: List[Tuple[int, int, str, int, int]] = []
    previous_key: Tuple[int, int] | None = None
    current_rank = 0

    for index, (user_id, username, points, perfect_predictions) in enumerate(rows, start=1):
        key = (points, perfect_predictions)
        if previous_key is None or key != previous_key:
            current_rank = index
        ranked.append((current_rank, user_id, username, points, perfect_predictions))
        previous_key = key

    return ranked


async def get_user_prediction_totals(db: AsyncSession, user_id: int) -> Tuple[int, int]:
    """Return (total_points, perfect_predictions) for a user across all games."""
    points_result = await db.execute(
        select(func.coalesce(func.sum(Prediction.points), 0)).where(Prediction.user_id == user_id)
    )
    total_points = int(points_result.scalar_one())

    perfect_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.user_id == user_id,
            Prediction.points == 100,
        )
    )
    perfect_predictions = int(perfect_result.scalar_one())

    return total_points, perfect_predictions


async def create_league_member(
    db: AsyncSession,
    league: League,
    user_id: int,
) -> LeagueMember:
    """Add a user to a league, storing score baselines when required."""
    points_at_join = 0
    perfect_predictions_at_join = 0
    if league.members_start_at_zero:
        points_at_join, perfect_predictions_at_join = await get_user_prediction_totals(db, user_id)

    member = LeagueMember(
        league_id=league.id,
        user_id=user_id,
        points_at_join=points_at_join,
        perfect_predictions_at_join=perfect_predictions_at_join,
    )
    db.add(member)
    return member


async def get_league_rankings(db: AsyncSession, league_id: int) -> List[LeagueRankingRow]:
    """
    Return league standings as (user_id, username, total_points, perfect_predictions)
    sorted by points desc, perfect predictions desc, then username asc.
    """
    league_result = await db.execute(select(League).where(League.id == league_id))
    league = league_result.scalar_one_or_none()
    if not league:
        return []

    points_subquery = (
        select(
            Prediction.user_id.label("user_id"),
            func.coalesce(func.sum(Prediction.points), 0).label("total_points"),
        )
        .group_by(Prediction.user_id)
        .subquery()
    )

    perfect_subquery = (
        select(
            Prediction.user_id.label("user_id"),
            func.count(Prediction.id).label("perfect_predictions"),
        )
        .where(Prediction.points == 100)
        .group_by(Prediction.user_id)
        .subquery()
    )

    raw_points = func.coalesce(points_subquery.c.total_points, 0)
    raw_perfect = func.coalesce(perfect_subquery.c.perfect_predictions, 0)

    if league.members_start_at_zero:
        total_points_expr = func.greatest(raw_points - LeagueMember.points_at_join, 0)
        perfect_predictions_expr = func.greatest(
            raw_perfect - LeagueMember.perfect_predictions_at_join,
            0,
        )
    else:
        total_points_expr = raw_points
        perfect_predictions_expr = raw_perfect

    result = await db.execute(
        select(
            User.id,
            User.username,
            total_points_expr.label("total_points"),
            perfect_predictions_expr.label("perfect_predictions"),
        )
        .join(LeagueMember, LeagueMember.user_id == User.id)
        .outerjoin(points_subquery, points_subquery.c.user_id == User.id)
        .outerjoin(perfect_subquery, perfect_subquery.c.user_id == User.id)
        .where(LeagueMember.league_id == league_id)
        .order_by(
            total_points_expr.desc(),
            perfect_predictions_expr.desc(),
            User.username.asc(),
        )
    )

    return [
        (row.id, row.username, int(row.total_points), int(row.perfect_predictions))
        for row in result.all()
    ]


async def sync_league_member_points(db: AsyncSession, user_id: int) -> None:
    """Update cached total_points on all league memberships for a user."""
    total_points, _ = await get_user_prediction_totals(db, user_id)

    members_result = await db.execute(select(LeagueMember).where(LeagueMember.user_id == user_id))
    for member in members_result.scalars().all():
        member.total_points = total_points


def game_counts_for_league_member(game, joined_at: datetime) -> bool:
    """True when a finished game's result should count toward league standings."""
    from app.db.models.game import GameStatus

    if game.status != GameStatus.FINISHED:
        return False

    if game.scheduled_at is not None:
        return game.scheduled_at >= joined_at

    if game.match_date is not None:
        return datetime.combine(game.match_date, time.min) >= joined_at

    return True


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

    league_result = await db.execute(select(League).where(League.id == invitation.league_id))
    league = league_result.scalar_one_or_none()
    if not league:
        raise ValueError("League not found")
    if league.is_join_locked:
        raise ValueError("This league is not accepting new members")

    existing = await db.execute(
        select(LeagueMember).where(
            LeagueMember.league_id == invitation.league_id,
            LeagueMember.user_id == user.id,
        )
    )
    if not existing.scalar_one_or_none():
        await create_league_member(db, league, user.id)

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
