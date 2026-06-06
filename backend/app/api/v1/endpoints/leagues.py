"""
League endpoints for creating and browsing prediction leagues.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import League, LeagueMember, User
from app.schemas.league import LeagueCreate, LeagueCreateResponse, LeagueSummary

router = APIRouter()


def _league_summary(league: League, member_count: int, is_member: bool) -> LeagueSummary:
    return LeagueSummary(
        id=league.id,
        name=league.name,
        description=league.description,
        is_private=league.is_private,
        created_at=league.created_at,
        member_count=member_count,
        is_member=is_member,
    )


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
        id=league.id,
        name=league.name,
        description=league.description,
        is_private=league.is_private,
        created_at=league.created_at,
        member_count=1,
        invite_code=league.invite_code,
    )


@router.post("/{league_id}/join", response_model=LeagueSummary)
async def join_league(
    league_id: int,
    invite_code: Optional[str] = Query(None, max_length=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a public league, or a private league with the correct password."""
    result = await db.execute(
        select(League).options(selectinload(League.members)).where(League.id == league_id)
    )
    league = result.scalar_one_or_none()
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")

    existing = await db.execute(
        select(LeagueMember).where(
            LeagueMember.league_id == league_id,
            LeagueMember.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this league")

    if league.is_private:
        if not invite_code or invite_code != league.invite_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid league password")

    db.add(LeagueMember(league_id=league.id, user_id=current_user.id))
    await db.commit()

    count_result = await db.execute(
        select(func.count(LeagueMember.id)).where(LeagueMember.league_id == league.id)
    )
    member_count = count_result.scalar_one()

    return _league_summary(league, member_count, is_member=True)
