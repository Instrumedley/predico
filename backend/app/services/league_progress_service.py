"""
Build cumulative league progress series for the progress chart.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Game, Prediction
from app.db.models.game import GameStatus
from app.schemas.league import (
    LeagueProgressMatch,
    LeagueProgressMatchTeam,
    LeagueProgressMember,
    LeagueProgressResponse,
)
from app.services.league_service import assign_league_ranks, get_league_rankings


def _match_label(home_code: str, away_code: str) -> str:
    return f"{home_code} v {away_code}"


async def build_league_progress(
    db: AsyncSession,
    league_id: int,
    current_user_id: int,
) -> LeagueProgressResponse:
    """Return cumulative points per finished match for league members."""
    rankings = await get_league_rankings(db, league_id)
    if not rankings:
        return LeagueProgressResponse(matches=[], members=[], has_scored_matches=False)

    top_five_ids = {user_id for user_id, _, _, _ in rankings[:5]}

    games_result = await db.execute(
        select(Game)
        .where(Game.status == GameStatus.FINISHED)
        .options(
            selectinload(Game.home_team),
            selectinload(Game.away_team),
        )
        .order_by(
            Game.match_number.asc().nulls_last(),
            Game.match_date.asc(),
            Game.match_time.asc(),
            Game.id.asc(),
        )
    )
    games = games_result.scalars().all()

    points_by_user_game: Dict[Tuple[int, int], int] = {}
    if games:
        game_ids = [game.id for game in games]
        member_ids = [user_id for user_id, _, _, _ in rankings]
        predictions_result = await db.execute(
            select(Prediction.user_id, Prediction.game_id, Prediction.points).where(
                Prediction.user_id.in_(member_ids),
                Prediction.game_id.in_(game_ids),
            )
        )
        points_by_user_game = {
            (user_id, game_id): int(points or 0)
            for user_id, game_id, points in predictions_result.all()
        }

    matches: List[LeagueProgressMatch] = []
    for game in games:
        home = game.home_team
        away = game.away_team
        matches.append(
            LeagueProgressMatch(
                game_id=game.id,
                match_number=game.match_number,
                match_date=game.match_date,
                home_team=LeagueProgressMatchTeam(
                    id=home.id,
                    name=home.name,
                    country_code=home.country_code,
                    flag_emoji=home.flag_emoji,
                ),
                away_team=LeagueProgressMatchTeam(
                    id=away.id,
                    name=away.name,
                    country_code=away.country_code,
                    flag_emoji=away.flag_emoji,
                ),
                label=_match_label(home.country_code, away.country_code),
            )
        )

    members: List[LeagueProgressMember] = []

    for rank, user_id, username, total_points, _ in assign_league_ranks(rankings):
        cumulative = [0]
        for game in games:
            match_points = points_by_user_game.get((user_id, game.id), 0)
            cumulative.append(cumulative[-1] + match_points)

        members.append(
            LeagueProgressMember(
                user_id=user_id,
                username=username,
                rank=rank,
                total_points=total_points,
                is_top_five=user_id in top_five_ids,
                is_current_user=user_id == current_user_id,
                points=cumulative,
            )
        )

    return LeagueProgressResponse(
        matches=matches,
        members=members,
        has_scored_matches=len(matches) > 0,
    )
