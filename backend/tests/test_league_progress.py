"""Tests for league cumulative progress chart data."""
from datetime import date, datetime, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models.game import Game, GameStatus
from app.db.models.team import Team
from app.services.league_progress_service import build_league_progress


@pytest.mark.asyncio
async def test_build_league_progress_cumulative_points():
    home = Team(id=1, name="Mexico", country_code="MEX", flag_emoji="🇲🇽")
    away = Team(id=2, name="South Africa", country_code="ZAF", flag_emoji="🇿🇦")
    game_one = Game(
        id=10,
        home_team_id=1,
        away_team_id=2,
        home_team=home,
        away_team=away,
        scheduled_at=datetime(2026, 6, 11, 19, 0),
        match_date=date(2026, 6, 11),
        match_time=time(13, 0),
        timezone="UTC-6",
        status=GameStatus.FINISHED,
        round_id=1,
        match_number=1,
    )
    game_two = Game(
        id=11,
        home_team_id=2,
        away_team_id=1,
        home_team=away,
        away_team=home,
        scheduled_at=datetime(2026, 6, 12, 19, 0),
        match_date=date(2026, 6, 12),
        match_time=time(13, 0),
        timezone="UTC-6",
        status=GameStatus.FINISHED,
        round_id=1,
        match_number=2,
    )

    db = AsyncMock()
    call_count = 0

    with patch(
        "app.services.league_progress_service.get_league_rankings",
        new=AsyncMock(return_value=[(1, "alice", 150), (2, "bob", 50)]),
    ):
        games_result = MagicMock()
        games_scalars = MagicMock()
        games_scalars.all.return_value = [game_one, game_two]
        games_result.scalars.return_value = games_scalars

        predictions_result = MagicMock()
        predictions_result.all.return_value = [
            (1, 10, 100),
            (1, 11, 50),
            (2, 10, 50),
            (2, 11, 0),
        ]

        async def execute_side_effect(_query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return games_result
            return predictions_result

        db.execute = AsyncMock(side_effect=execute_side_effect)

        progress = await build_league_progress(db, league_id=1, current_user_id=2)

    assert progress.has_scored_matches is True
    assert len(progress.matches) == 2
    assert progress.matches[0].label == "MEX v ZAF"

    alice = next(member for member in progress.members if member.username == "alice")
    bob = next(member for member in progress.members if member.username == "bob")

    assert alice.points == [0, 100, 150]
    assert bob.points == [0, 50, 50]
    assert alice.is_top_five is True
    assert bob.is_current_user is True
