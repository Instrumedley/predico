"""Build the knockout bracket from group standings and admin match results."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.knockout_result import KnockoutMatchResult
from app.services.knockout.bracket_structure import (
    LEFT_QF_ORDER,
    LEFT_R16_ORDER,
    LEFT_R32_ORDER,
    RIGHT_QF_ORDER,
    RIGHT_R16_ORDER,
    RIGHT_R32_ORDER,
    BracketMatchDef,
    BracketSlotDef,
    KNOCKOUT_MATCH_DEFS,
    THIRD_PLACE_WINNER_GROUPS,
)
from app.services.knockout.standings_helpers import (
    GroupStandings,
    TeamStanding,
    get_team_at_position,
    load_group_standings,
    rank_third_place_teams,
)
from app.services.knockout.third_place import (
    format_third_place_candidates,
    format_third_place_group,
    lookup_third_place_assignments,
)


@dataclass
class ResolvedTeam:
    team_id: int
    country_code: str
    country_name: str
    flag_emoji: str | None


@dataclass
class ResolvedSlot:
    label: str | None = None
    team: ResolvedTeam | None = None


@dataclass
class ResolvedMatch:
    match_number: int
    home: ResolvedSlot
    away: ResolvedSlot
    home_score: int | None = None
    away_score: int | None = None
    winner_team_id: int | None = None
    is_finished: bool = False


@dataclass
class BracketSideData:
    round_of32: list[ResolvedMatch]
    round_of16: list[ResolvedMatch]
    quarter_finals: list[ResolvedMatch]
    semi_final: ResolvedMatch


@dataclass
class KnockoutBracketResponse:
    left: BracketSideData
    right: BracketSideData
    final: ResolvedMatch
    third_place: ResolvedMatch
    third_place_combination_key: str | None = None


@dataclass
class _BuildContext:
    standings_by_group: dict[str, GroupStandings]
    third_place_assignments: dict[str, str] | None
    qualifying_third_groups: set[str]
    resolved_matches: dict[int, ResolvedMatch] = field(default_factory=dict)
    results_by_match: dict[int, KnockoutMatchResult] = field(default_factory=dict)


async def load_knockout_results(db: AsyncSession) -> dict[int, KnockoutMatchResult]:
    query = select(KnockoutMatchResult).options(
        selectinload(KnockoutMatchResult.winner_team),
    )
    result = await db.execute(query)
    return {row.match_number: row for row in result.scalars().all()}


def _team_from_standing(standing: TeamStanding) -> ResolvedTeam:
    return ResolvedTeam(
        team_id=standing.team_id,
        country_code=standing.country_code,
        country_name=standing.country_name,
        flag_emoji=standing.flag_emoji,
    )


def _slot_with_team(team: ResolvedTeam) -> ResolvedSlot:
    return ResolvedSlot(team=team)


def _slot_with_label(label: str) -> ResolvedSlot:
    return ResolvedSlot(label=label)


def _empty_slot() -> ResolvedSlot:
    return ResolvedSlot()


def _winner_label(group: str) -> str:
    return f"Winner Group {group}"


def _runner_up_label(group: str) -> str:
    return f"Runner-up Group {group}"


def _resolve_group_slot(
    context: _BuildContext,
    slot: BracketSlotDef,
    *,
    position: int,
    label_builder,
) -> ResolvedSlot:
    if not slot.group:
        return _empty_slot()

    group = context.standings_by_group.get(slot.group)
    if not group or not group.is_complete:
        return _slot_with_label(label_builder(slot.group))

    standing = get_team_at_position(group, position)
    if not standing:
        return _slot_with_label(label_builder(slot.group))

    return _slot_with_team(_team_from_standing(standing))


def _resolve_best_third_slot(
    context: _BuildContext,
    slot: BracketSlotDef,
    match_def: BracketMatchDef,
) -> ResolvedSlot:
    if not slot.candidate_groups:
        return _empty_slot()

    winner_group = match_def.home.group
    if winner_group not in THIRD_PLACE_WINNER_GROUPS:
        return _slot_with_label(format_third_place_candidates(slot.candidate_groups))

    if context.third_place_assignments and winner_group in context.third_place_assignments:
        assigned_group = context.third_place_assignments[winner_group]
        if assigned_group not in context.qualifying_third_groups:
            return _slot_with_label(format_third_place_group(assigned_group))

        group = context.standings_by_group.get(assigned_group)
        if group and group.is_complete:
            third = get_team_at_position(group, 3)
            if third:
                return _slot_with_team(_team_from_standing(third))

        return _slot_with_label(format_third_place_group(assigned_group))

    return _slot_with_label(format_third_place_candidates(slot.candidate_groups))


def _resolve_slot(context: _BuildContext, match_def: BracketMatchDef, slot: BracketSlotDef) -> ResolvedSlot:
    if slot.kind == "winner":
        return _resolve_group_slot(context, slot, position=1, label_builder=_winner_label)
    if slot.kind == "runner_up":
        return _resolve_group_slot(context, slot, position=2, label_builder=_runner_up_label)
    if slot.kind == "best_third":
        return _resolve_best_third_slot(context, slot, match_def)
    if slot.kind in {"match_winner", "match_loser"}:
        source_match = slot.source_match
        if not source_match:
            return _empty_slot()

        prefix = "Winner" if slot.kind == "match_winner" else "Loser"
        label = f"{prefix} Match {source_match}"

        if source_match not in context.resolved_matches:
            return _slot_with_label(label)

        source = context.resolved_matches[source_match]
        result = context.results_by_match.get(source_match)
        if not result or not result.winner_team_id:
            return _slot_with_label(label)

        home_team = source.home.team
        away_team = source.away.team
        if not home_team or not away_team:
            return _slot_with_label(label)

        if slot.kind == "match_winner":
            winner = home_team if result.winner_team_id == home_team.team_id else away_team
            return _slot_with_team(winner)

        loser = away_team if result.winner_team_id == home_team.team_id else home_team
        return _slot_with_team(loser)

    return _empty_slot()


def _apply_result(match: ResolvedMatch, result: KnockoutMatchResult | None) -> None:
    if not result:
        return

    match.home_score = result.home_score
    match.away_score = result.away_score
    match.winner_team_id = result.winner_team_id
    match.is_finished = result.winner_team_id is not None


def _build_match(context: _BuildContext, match_number: int) -> ResolvedMatch:
    match_def = KNOCKOUT_MATCH_DEFS[match_number]
    resolved = ResolvedMatch(
        match_number=match_number,
        home=_resolve_slot(context, match_def, match_def.home),
        away=_resolve_slot(context, match_def, match_def.away),
    )
    _apply_result(resolved, context.results_by_match.get(match_number))
    context.resolved_matches[match_number] = resolved
    return resolved


async def _build_knockout_context(db: AsyncSession) -> _BuildContext:
    standings_by_group = await load_group_standings(db)
    results_by_match = await load_knockout_results(db)

    ranked_third = rank_third_place_teams(standings_by_group)
    qualifying_third_groups: set[str] = set()
    third_place_assignments: dict[str, str] | None = None

    if len(ranked_third) == 12:
        top_eight = ranked_third[:8]
        qualifying_third_groups = {group_letter for group_letter, _ in top_eight}
        third_place_assignments = lookup_third_place_assignments(qualifying_third_groups)

    context = _BuildContext(
        standings_by_group=standings_by_group,
        third_place_assignments=third_place_assignments,
        qualifying_third_groups=qualifying_third_groups,
        results_by_match=results_by_match,
    )

    for match_number in sorted(KNOCKOUT_MATCH_DEFS):
        _build_match(context, match_number)

    return context


async def resolve_all_knockout_matches(db: AsyncSession) -> dict[int, ResolvedMatch]:
    """Resolve every knockout match slot (teams and/or bracket labels)."""
    context = await _build_knockout_context(db)
    return context.resolved_matches


async def build_knockout_bracket(db: AsyncSession) -> KnockoutBracketResponse:
    context = await _build_knockout_context(db)
    combination_key: str | None = None
    if len(context.qualifying_third_groups) == 8:
        combination_key = "".join(sorted(context.qualifying_third_groups))

    return KnockoutBracketResponse(
        left=BracketSideData(
            round_of32=[context.resolved_matches[n] for n in LEFT_R32_ORDER],
            round_of16=[context.resolved_matches[n] for n in LEFT_R16_ORDER],
            quarter_finals=[context.resolved_matches[n] for n in LEFT_QF_ORDER],
            semi_final=context.resolved_matches[101],
        ),
        right=BracketSideData(
            round_of32=[context.resolved_matches[n] for n in RIGHT_R32_ORDER],
            round_of16=[context.resolved_matches[n] for n in RIGHT_R16_ORDER],
            quarter_finals=[context.resolved_matches[n] for n in RIGHT_QF_ORDER],
            semi_final=context.resolved_matches[102],
        ),
        final=context.resolved_matches[104],
        third_place=context.resolved_matches[103],
        third_place_combination_key=combination_key,
    )


def bracket_to_api_dict(bracket: KnockoutBracketResponse) -> dict:
    def slot_to_dict(slot: ResolvedSlot) -> dict:
        payload: dict = {}
        if slot.label:
            payload["label"] = slot.label
        if slot.team:
            payload["team"] = {
                "team_id": slot.team.team_id,
                "country_code": slot.team.country_code,
                "country_name": slot.team.country_name,
                "flag_emoji": slot.team.flag_emoji,
            }
        return payload

    def match_to_dict(match: ResolvedMatch) -> dict:
        return {
            "match_number": match.match_number,
            "home": slot_to_dict(match.home),
            "away": slot_to_dict(match.away),
            "home_score": match.home_score,
            "away_score": match.away_score,
            "winner_team_id": match.winner_team_id,
            "is_finished": match.is_finished,
        }

    def side_to_dict(side: BracketSideData) -> dict:
        return {
            "round_of32": [match_to_dict(match) for match in side.round_of32],
            "round_of16": [match_to_dict(match) for match in side.round_of16],
            "quarter_finals": [match_to_dict(match) for match in side.quarter_finals],
            "semi_final": match_to_dict(side.semi_final),
        }

    return {
        "left": side_to_dict(bracket.left),
        "right": side_to_dict(bracket.right),
        "final": match_to_dict(bracket.final),
        "third_place": match_to_dict(bracket.third_place),
        "third_place_combination_key": bracket.third_place_combination_key,
    }
