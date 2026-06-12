"""
League endpoints for creating and browsing prediction leagues.
"""
import re
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Game, League, LeagueMember, Prediction, User
from app.api.v1.endpoints.games import game_to_response
from app.schemas.league import (
    AcceptLeagueInviteRequest,
    JoinLeagueRequest,
    LeagueCreate,
    LeagueCreateResponse,
    LeagueDetail,
    LeagueInviteRequest,
    LeagueInviteResponse,
    LeagueMemberPrediction,
    LeagueMemberPredictionGame,
    LeagueMemberPredictionTeam,
    LeagueMemberPredictionsResponse,
    LeagueMemberRanking,
    LeagueProgressResponse,
    LeagueSummary,
)
from app.services.league_progress_service import build_league_progress
from app.services.email_service import email_service
from app.services.league_service import (
    accept_league_invitation,
    accept_pending_invites_for_user,
    create_or_refresh_league_invitation,
    get_invitation_by_token,
    get_league_rankings,
)

router = APIRouter()


def _league_summary(league: League, member_count: int, is_member: bool) -> LeagueSummary:
    return LeagueSummary(
        id=league.public_id,
        name=league.name,
        description=league.description,
        is_private=league.is_private,
        created_at=league.created_at,
        member_count=member_count,
        is_member=is_member,
    )


def _normalize_emails(raw_emails: List[str]) -> List[str]:
    seen = set()
    normalized: List[str] = []
    for raw in raw_emails:
        for part in re.split(r"[,;\s]+", raw):
            email = part.strip().lower()
            if not email or email in seen:
                continue
            try:
                validated = validate_email(email, check_deliverability=False)
                normalized_email = validated.email
            except EmailNotValidError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid email address: {email}",
                ) from exc
            seen.add(normalized_email)
            normalized.append(normalized_email)
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one valid email address",
        )
    if len(normalized) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can invite up to 20 email addresses at once",
        )
    return normalized


async def _get_league_or_404(db: AsyncSession, league_id: UUID) -> League:
    result = await db.execute(select(League).where(League.public_id == league_id))
    league = result.scalar_one_or_none()
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")
    return league


async def _get_member_counts(db: AsyncSession, league_ids: List[int]) -> dict[int, int]:
    if not league_ids:
        return {}
    result = await db.execute(
        select(LeagueMember.league_id, func.count(LeagueMember.id))
        .where(LeagueMember.league_id.in_(league_ids))
        .group_by(LeagueMember.league_id)
    )
    return {league_id: count for league_id, count in result.all()}


async def _get_user_memberships(db: AsyncSession, user_id: int, league_ids: List[int]) -> set[int]:
    if not league_ids:
        return set()
    result = await db.execute(
        select(LeagueMember.league_id).where(
            LeagueMember.user_id == user_id,
            LeagueMember.league_id.in_(league_ids),
        )
    )
    return {row[0] for row in result.all()}


async def _require_league_member(
    db: AsyncSession,
    league_id: int,
    user_id: int,
    *,
    detail: str = "You must be a member of this league",
) -> None:
    result = await db.execute(
        select(LeagueMember.id).where(
            LeagueMember.league_id == league_id,
            LeagueMember.user_id == user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _require_league_creator(league: League, user: User) -> None:
    if league.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the league creator can perform this action",
        )


def _ensure_league_accepts_joins(league: League) -> None:
    if league.is_join_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This league is not accepting new members",
        )


def _prediction_to_league_member_prediction(prediction: Prediction) -> LeagueMemberPrediction:
    game_response = game_to_response(prediction.game)
    home_team = game_response.home_team
    away_team = game_response.away_team
    return LeagueMemberPrediction(
        id=prediction.id,
        predicted_home_score=prediction.predicted_home_score,
        predicted_away_score=prediction.predicted_away_score,
        points=prediction.points,
        game=LeagueMemberPredictionGame(
            id=game_response.id,
            status=game_response.status,
            match_date=game_response.match_date,
            scheduled_at=game_response.scheduled_at,
            home_team=LeagueMemberPredictionTeam(
                id=home_team.id,
                name=home_team.name,
                country_code=home_team.country_code,
            ),
            away_team=LeagueMemberPredictionTeam(
                id=away_team.id,
                name=away_team.name,
                country_code=away_team.country_code,
            ),
        ),
    )


async def _build_rankings(db: AsyncSession, league_id: int) -> List[LeagueMemberRanking]:
    rows = await get_league_rankings(db, league_id)
    rankings: List[LeagueMemberRanking] = []
    previous_points: Optional[int] = None
    current_rank = 0

    for index, (user_id, username, points, perfect_predictions) in enumerate(rows, start=1):
        if previous_points is None or points != previous_points:
            current_rank = index
        rankings.append(
            LeagueMemberRanking(
                rank=current_rank,
                user_id=user_id,
                username=username,
                total_points=points,
                perfect_predictions=perfect_predictions,
            )
        )
        previous_points = points

    return rankings


async def _build_league_detail(
    db: AsyncSession,
    league: League,
    current_user: User,
    *,
    is_member: Optional[bool] = None,
) -> LeagueDetail:
    if is_member is None:
        membership = await db.execute(
            select(LeagueMember).where(
                LeagueMember.league_id == league.id,
                LeagueMember.user_id == current_user.id,
            )
        )
        is_member = membership.scalar_one_or_none() is not None

    member_count = await _get_member_counts(db, [league.id])
    rankings = await _build_rankings(db, league.id) if is_member else []

    return LeagueDetail(
        id=league.public_id,
        name=league.name,
        description=league.description,
        is_private=league.is_private,
        is_join_locked=league.is_join_locked,
        created_at=league.created_at,
        created_by=league.created_by,
        member_count=member_count.get(league.id, 0),
        is_member=is_member,
        is_creator=league.created_by == current_user.id,
        rankings=rankings,
    )


@router.get("/me", response_model=List[LeagueSummary])
async def list_my_leagues(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Leagues the current user belongs to."""
    result = await db.execute(
        select(League)
        .join(LeagueMember, LeagueMember.league_id == League.id)
        .where(LeagueMember.user_id == current_user.id)
        .order_by(League.name)
    )
    leagues = result.scalars().unique().all()
    league_ids = [league.id for league in leagues]
    counts = await _get_member_counts(db, league_ids)

    return [
        _league_summary(league, counts.get(league.id, 0), is_member=True)
        for league in leagues
    ]


@router.get("", response_model=List[LeagueSummary])
async def list_leagues(
    search: Optional[str] = Query(None, max_length=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """All leagues in the system, optionally filtered by name."""
    query = select(League).order_by(League.created_at.desc())
    if search and search.strip():
        query = query.where(League.name.ilike(f"%{search.strip()}%"))

    result = await db.execute(query)
    leagues = result.scalars().all()
    league_ids = [league.id for league in leagues]
    counts = await _get_member_counts(db, league_ids)
    memberships = await _get_user_memberships(db, current_user.id, league_ids)

    return [
        _league_summary(league, counts.get(league.id, 0), league.id in memberships)
        for league in leagues
    ]


@router.post("/accept-invite", response_model=LeagueDetail)
async def accept_league_invite(
    payload: AcceptLeagueInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept a league invitation using the token from the invite email."""
    invitation = await get_invitation_by_token(db, payload.token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation",
        )

    if invitation.invitee_email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation was sent to a different email address",
        )

    result = await db.execute(select(League).where(League.id == invitation.league_id))
    league = result.scalar_one_or_none()
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")

    _ensure_league_accepts_joins(league)

    if invitation.status == "accepted":
        membership = await db.execute(
            select(LeagueMember).where(
                LeagueMember.league_id == league.id,
                LeagueMember.user_id == current_user.id,
            )
        )
        if not membership.scalar_one_or_none():
            db.add(LeagueMember(league_id=league.id, user_id=current_user.id))
            await db.commit()
        return await _build_league_detail(db, league, current_user, is_member=True)

    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation",
        )
    if invitation.expires_at and invitation.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    try:
        await accept_league_invitation(db, invitation, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await db.commit()
    return await _build_league_detail(db, league, current_user, is_member=True)


@router.get("/{league_id}", response_model=LeagueDetail)
async def get_league_detail(
    league_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """League detail with member rankings for league members."""
    league = await _get_league_or_404(db, league_id)
    return await _build_league_detail(db, league, current_user)


@router.get("/{league_id}/progress", response_model=LeagueProgressResponse)
async def get_league_progress(
    league_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cumulative points by finished match for league members (feature-flagged)."""
    if not settings.LEAGUE_PROGRESS_CHART_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    league = await _get_league_or_404(db, league_id)
    await _require_league_member(db, league.id, current_user.id)
    return await build_league_progress(db, league.id, current_user.id)


@router.get("/{league_id}/members/{user_id}/predictions", response_model=LeagueMemberPredictionsResponse)
async def get_league_member_predictions(
    league_id: UUID,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a league member's predictions for other members of the same league."""
    league = await _get_league_or_404(db, league_id)
    await _require_league_member(db, league.id, current_user.id)

    target_user_result = await db.execute(select(User).where(User.id == user_id))
    target_user = target_user_result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await _require_league_member(
        db,
        league.id,
        user_id,
        detail="User is not a member of this league",
    )

    predictions_query = (
        select(Prediction)
        .where(Prediction.user_id == user_id)
        .options(
            selectinload(Prediction.game).selectinload(Game.home_team),
            selectinload(Prediction.game).selectinload(Game.away_team),
            selectinload(Prediction.game).selectinload(Game.round),
            selectinload(Prediction.game).selectinload(Game.group),
            selectinload(Prediction.game).selectinload(Game.stadium),
        )
        .join(Game, Prediction.game_id == Game.id)
        .order_by(Game.match_date.asc(), Game.match_time.asc())
    )
    predictions_result = await db.execute(predictions_query)
    predictions = predictions_result.scalars().all()

    total_points = sum(prediction.points for prediction in predictions)

    return LeagueMemberPredictionsResponse(
        user_id=target_user.id,
        username=target_user.username,
        total_points=total_points,
        predictions=[_prediction_to_league_member_prediction(prediction) for prediction in predictions],
    )


@router.post("", response_model=LeagueCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_league(
    payload: LeagueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a league and add the creator as the first member."""
    existing = await db.execute(select(League).where(League.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A league with this name already exists",
        )

    invite_code = payload.password if payload.is_private else None
    if invite_code:
        code_taken = await db.execute(select(League).where(League.invite_code == invite_code))
        if code_taken.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This password is already used by another league. Choose a different one.",
            )

    league = League(
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        created_by=current_user.id,
        is_private=payload.is_private,
        invite_code=invite_code,
    )
    db.add(league)
    await db.flush()

    db.add(LeagueMember(league_id=league.id, user_id=current_user.id))
    await db.commit()
    await db.refresh(league)

    return LeagueCreateResponse(
        id=league.public_id,
        name=league.name,
        description=league.description,
        is_private=league.is_private,
        created_at=league.created_at,
        member_count=1,
        invite_code=league.invite_code,
    )


@router.post("/{league_id}/join", response_model=LeagueDetail)
async def join_league(
    league_id: UUID,
    payload: Optional[JoinLeagueRequest] = None,
    invite_code: Optional[str] = Query(None, max_length=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a public league, or a private league with the correct password."""
    league = await _get_league_or_404(db, league_id)
    _ensure_league_accepts_joins(league)

    existing = await db.execute(
        select(LeagueMember).where(
            LeagueMember.league_id == league.id,
            LeagueMember.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this league")

    code = payload.invite_code if payload and payload.invite_code else invite_code
    if league.is_private:
        if not code or code != league.invite_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid league password")

    db.add(LeagueMember(league_id=league.id, user_id=current_user.id))
    await db.commit()

    return await _build_league_detail(db, league, current_user, is_member=True)


@router.post("/{league_id}/invitations", response_model=LeagueInviteResponse)
async def invite_to_league(
    league_id: UUID,
    payload: LeagueInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send league invitation emails. Only the league creator can invite."""
    league = await _get_league_or_404(db, league_id)

    _require_league_creator(league, current_user)
    _ensure_league_accepts_joins(league)

    emails = _normalize_emails(payload.emails)
    sent: List[str] = []
    failed: List[str] = []

    for email in emails:
        member_result = await db.execute(
            select(LeagueMember)
            .join(User, User.id == LeagueMember.user_id)
            .where(LeagueMember.league_id == league.id, User.email == email)
        )
        if member_result.scalar_one_or_none():
            sent.append(email)
            continue

        user_result = await db.execute(select(User).where(User.email == email))
        invitee = user_result.scalar_one_or_none()
        invite_token = await create_or_refresh_league_invitation(
            db,
            league_id=league.id,
            inviter_id=current_user.id,
            invitee_email=email,
        )
        success = await email_service.send_league_invite_email(
            email=email,
            league_name=league.name,
            league_description=league.description,
            inviter_name=current_user.username,
            league_public_id=league.public_id,
            is_private=league.is_private,
            invite_token=invite_token,
            recipient_name=invitee.username if invitee else None,
        )
        if success:
            sent.append(email)
        else:
            failed.append(email)

    if sent or failed:
        await db.commit()

    if not sent and failed:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send invitation emails. Check email configuration.",
        )

    return LeagueInviteResponse(sent=sent, failed=failed)


@router.delete("/{league_id}/members/{user_id}", response_model=LeagueDetail)
async def remove_league_member(
    league_id: UUID,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from the league. Only the league creator can remove members."""
    league = await _get_league_or_404(db, league_id)
    _require_league_creator(league, current_user)

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from the league",
        )

    member_result = await db.execute(
        select(LeagueMember).where(
            LeagueMember.league_id == league.id,
            LeagueMember.user_id == user_id,
        )
    )
    member = member_result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not a member of this league")

    await db.delete(member)
    await db.commit()

    return await _build_league_detail(db, league, current_user, is_member=True)


@router.post("/{league_id}/lock", response_model=LeagueDetail)
async def lock_league_joins(
    league_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Prevent new members from joining the league."""
    league = await _get_league_or_404(db, league_id)
    _require_league_creator(league, current_user)

    league.is_join_locked = True
    await db.commit()
    await db.refresh(league)

    return await _build_league_detail(db, league, current_user, is_member=True)


@router.post("/{league_id}/unlock", response_model=LeagueDetail)
async def unlock_league_joins(
    league_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allow new members to join the league again."""
    league = await _get_league_or_404(db, league_id)
    _require_league_creator(league, current_user)

    league.is_join_locked = False
    await db.commit()
    await db.refresh(league)

    return await _build_league_detail(db, league, current_user, is_member=True)
