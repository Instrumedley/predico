"""Tests for league reset-on-join scoring."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models.game import GameStatus
from app.db.models.league import League, LeagueMember
from app.services.league_service import assign_league_ranks, get_league_rankings


@pytest.mark.asyncio
async def test_get_league_rankings_subtracts_baseline_when_reset_enabled():
    league = League(id=1, members_start_at_zero=True)
    league_result = MagicMock()
    league_result.scalar_one_or_none.return_value = league

    ranking_rows = [
        MagicMock(id=1, username="alice", total_points=150, perfect_predictions=1),
        MagicMock(id=2, username="bob", total_points=50, perfect_predictions=0),
    ]
    rankings_result = MagicMock()
    rankings_result.all.return_value = ranking_rows

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[league_result, rankings_result])

    rows = await get_league_rankings(db, league_id=1)

    assert rows == [(1, "alice", 150, 1), (2, "bob", 50, 0)]


def test_assign_league_ranks_with_reset_league_scores():
    rows = [
        (1, "alice", 0, 0),
        (2, "bob", 0, 0),
    ]

    ranked = assign_league_ranks(rows)

    assert ranked[0][0] == 1
    assert ranked[1][0] == 1
    assert ranked[0][3] == 0
    assert ranked[1][3] == 0


@pytest.mark.asyncio
async def test_build_league_progress_zeros_pre_join_matches_for_reset_league():
    from datetime import date, time

    from app.db.models.game import Game
    from app.db.models.team import Team
    from app.services.league_progress_service import build_league_progress

    league = League(id=1, members_start_at_zero=True)
    home = Team(id=1, name="Mexico", country_code="MEX", flag_emoji="🇲🇽")
    away = Team(id=2, name="South Africa", country_code="ZAF", flag_emoji="🇿🇦")

    early_game = Game(
        id=10,
        home_team_id=1,
        away_team_id=2,
        home_team=home,
        away_team=away,
        scheduled_at=datetime(2026, 6, 10, 19, 0),
        match_date=date(2026, 6, 10),
        match_time=time(13, 0),
        timezone="UTC-6",
        status=GameStatus.FINISHED,
        round_id=1,
        match_number=1,
    )
    late_game = Game(
        id=11,
        home_team_id=2,
        away_team_id=1,
        home_team=away,
        away_team=home,
        scheduled_at=datetime(2026, 6, 15, 19, 0),
        match_date=date(2026, 6, 15),
        match_time=time(13, 0),
        timezone="UTC-6",
        status=GameStatus.FINISHED,
        round_id=1,
        match_number=2,
    )

    member = LeagueMember(
        league_id=1,
        user_id=1,
        joined_at=datetime(2026, 6, 12, 12, 0),
        points_at_join=100,
        perfect_predictions_at_join=1,
    )

    db = AsyncMock()
    call_count = 0

    league_result = MagicMock()
    league_result.scalar_one_or_none.return_value = league

    members_result = MagicMock()
    members_result.scalars.return_value.all.return_value = [member]

    games_result = MagicMock()
    games_result.scalars.return_value.all.return_value = [early_game, late_game]

    predictions_result = MagicMock()
    predictions_result.all.return_value = [(1, 10, 100), (1, 11, 50)]

    with patch(
        "app.services.league_progress_service.get_league_rankings",
        new=AsyncMock(return_value=[(1, "alice", 50, 0)]),
    ):
        async def execute_side_effect(_query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return league_result
            if call_count == 2:
                return members_result
            if call_count == 3:
                return games_result
            return predictions_result

        db.execute = AsyncMock(side_effect=execute_side_effect)

        progress = await build_league_progress(db, league_id=1, current_user_id=1)

    alice = progress.members[0]
    assert alice.total_points == 50
    assert alice.points == [0, 0, 50]
    assert alice.match_points[0].points == 0
    assert alice.match_points[1].points == 50
