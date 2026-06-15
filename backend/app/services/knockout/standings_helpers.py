"""Helpers for reading group-stage standings used by the knockout bracket."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Game, Group, GroupTeam
from app.db.models.game import GameStatus


@dataclass
class TeamStanding:
    team_id: int
    country_code: str
    country_name: str
    flag_emoji: str | None
    position: int
    points: int
    goal_difference: int
    goals_for: int


@dataclass
class GroupStandings:
    group_letter: str
    is_complete: bool
    teams: list[TeamStanding]


async def load_group_standings(db: AsyncSession) -> dict[str, GroupStandings]:
    groups_query = select(Group).order_by(Group.name.asc())
    groups_result = await db.execute(groups_query)
    groups = groups_result.scalars().all()

    standings_by_group: dict[str, GroupStandings] = {}

    for group in groups:
        group_letter = group.name.replace("Group ", "").strip().upper()

        group_teams_query = (
            select(GroupTeam)
            .where(GroupTeam.group_id == group.id)
            .options(selectinload(GroupTeam.team))
        )
        group_teams_result = await db.execute(group_teams_query)
        group_teams = group_teams_result.scalars().all()

        total_games_query = select(func.count(Game.id)).where(Game.group_id == group.id)
        finished_games_query = select(func.count(Game.id)).where(
            Game.group_id == group.id,
            Game.status == GameStatus.FINISHED,
        )
        total_games = (await db.execute(total_games_query)).scalar_one()
        finished_games = (await db.execute(finished_games_query)).scalar_one()
        is_complete = total_games > 0 and finished_games == total_games

        team_stats: list[TeamStanding] = []

        for group_team in group_teams:
            team = group_team.team
            games_query = select(Game).where(
                Game.group_id == group.id,
                Game.status == GameStatus.FINISHED,
                or_(Game.home_team_id == team.id, Game.away_team_id == team.id),
            )
            games_result = await db.execute(games_query)
            games = games_result.scalars().all()

            wins = draws = losses = 0
            goals_for = goals_against = 0

            for game in games:
                is_home = game.home_team_id == team.id
                home_score = game.home_score or 0
                away_score = game.away_score or 0

                if is_home:
                    goals_for += home_score
                    goals_against += away_score
                    if home_score > away_score:
                        wins += 1
                    elif home_score == away_score:
                        draws += 1
                    else:
                        losses += 1
                else:
                    goals_for += away_score
                    goals_against += home_score
                    if away_score > home_score:
                        wins += 1
                    elif away_score == home_score:
                        draws += 1
                    else:
                        losses += 1

            team_stats.append(
                TeamStanding(
                    team_id=team.id,
                    country_code=team.country_code,
                    country_name=team.name,
                    flag_emoji=team.flag_emoji,
                    position=0,
                    points=wins * 3 + draws,
                    goal_difference=goals_for - goals_against,
                    goals_for=goals_for,
                )
            )

        team_stats.sort(
            key=lambda row: (row.points, row.goal_difference, row.goals_for),
            reverse=True,
        )
        for index, row in enumerate(team_stats, start=1):
            row.position = index

        standings_by_group[group_letter] = GroupStandings(
            group_letter=group_letter,
            is_complete=is_complete,
            teams=team_stats,
        )

    return standings_by_group


def get_team_at_position(group: GroupStandings, position: int) -> TeamStanding | None:
    for team in group.teams:
        if team.position == position:
            return team
    return None


def rank_third_place_teams(
    standings_by_group: dict[str, GroupStandings],
) -> list[tuple[str, TeamStanding]]:
    """Return third-place teams sorted best-to-worst (only from complete groups)."""
    third_place_rows: list[tuple[str, TeamStanding]] = []

    for group_letter, group in standings_by_group.items():
        if not group.is_complete:
            continue
        third = get_team_at_position(group, 3)
        if third:
            third_place_rows.append((group_letter, third))

    third_place_rows.sort(
        key=lambda item: (item[1].points, item[1].goal_difference, item[1].goals_for),
        reverse=True,
    )
    return third_place_rows
