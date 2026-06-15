"""Static 2026 World Cup knockout bracket structure (matches 73–104)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SlotKind = Literal[
    "winner",
    "runner_up",
    "best_third",
    "match_winner",
    "match_loser",
]

GROUP_LETTERS = list("ABCDEFGHIJKL")

# Winner slots that can face a best third-place team (matrix columns).
THIRD_PLACE_WINNER_GROUPS = ("A", "B", "D", "E", "G", "I", "K", "L")


@dataclass(frozen=True)
class BracketSlotDef:
    kind: SlotKind
    group: str | None = None
    candidate_groups: tuple[str, ...] | None = None
    source_match: int | None = None


@dataclass(frozen=True)
class BracketMatchDef:
    match_number: int
    home: BracketSlotDef
    away: BracketSlotDef
    round_key: Literal["r32", "r16", "qf", "sf", "final", "third_place"]
    side: Literal["left", "right", "center"] | None = None


def _winner(group: str) -> BracketSlotDef:
    return BracketSlotDef(kind="winner", group=group)


def _runner_up(group: str) -> BracketSlotDef:
    return BracketSlotDef(kind="runner_up", group=group)


def _best_third(*groups: str) -> BracketSlotDef:
    return BracketSlotDef(kind="best_third", candidate_groups=groups)


def _match_winner(match_number: int) -> BracketSlotDef:
    return BracketSlotDef(kind="match_winner", source_match=match_number)


def _match_loser(match_number: int) -> BracketSlotDef:
    return BracketSlotDef(kind="match_loser", source_match=match_number)


R32_MATCH_DEFS: dict[int, BracketMatchDef] = {
    # Visual left column (top → bottom) per FIFA 2026 bracket graphic
    73: BracketMatchDef(73, _runner_up("A"), _runner_up("B"), "r32", "left"),
    74: BracketMatchDef(74, _winner("E"), _best_third("A", "B", "C", "D", "F"), "r32", "left"),
    75: BracketMatchDef(75, _winner("F"), _runner_up("C"), "r32", "left"),
    77: BracketMatchDef(77, _winner("I"), _best_third("C", "D", "F", "G", "H"), "r32", "left"),
    81: BracketMatchDef(81, _winner("D"), _best_third("B", "E", "F", "I", "J"), "r32", "left"),
    82: BracketMatchDef(82, _winner("G"), _best_third("A", "E", "H", "I", "J"), "r32", "left"),
    83: BracketMatchDef(83, _runner_up("K"), _runner_up("L"), "r32", "left"),
    84: BracketMatchDef(84, _winner("H"), _runner_up("J"), "r32", "left"),
    # Visual right column (top → bottom)
    76: BracketMatchDef(76, _winner("C"), _runner_up("F"), "r32", "right"),
    78: BracketMatchDef(78, _runner_up("E"), _runner_up("I"), "r32", "right"),
    79: BracketMatchDef(79, _winner("A"), _best_third("C", "E", "F", "H", "I"), "r32", "right"),
    80: BracketMatchDef(80, _winner("L"), _best_third("E", "H", "I", "J", "K"), "r32", "right"),
    85: BracketMatchDef(85, _winner("B"), _best_third("E", "F", "G", "I", "J"), "r32", "right"),
    86: BracketMatchDef(86, _winner("J"), _runner_up("H"), "r32", "right"),
    87: BracketMatchDef(87, _winner("K"), _best_third("D", "E", "I", "J", "L"), "r32", "right"),
    88: BracketMatchDef(88, _runner_up("D"), _runner_up("G"), "r32", "right"),
}

KNOCKOUT_MATCH_DEFS: dict[int, BracketMatchDef] = {
    **R32_MATCH_DEFS,
    # R16 — each pair of adjacent R32 rows on the same side feeds one R16 slot (top → bottom)
    89: BracketMatchDef(89, _match_winner(74), _match_winner(77), "r16", "left"),
    90: BracketMatchDef(90, _match_winner(73), _match_winner(75), "r16", "left"),
    93: BracketMatchDef(93, _match_winner(83), _match_winner(84), "r16", "left"),
    94: BracketMatchDef(94, _match_winner(81), _match_winner(82), "r16", "left"),
    91: BracketMatchDef(91, _match_winner(76), _match_winner(78), "r16", "right"),
    92: BracketMatchDef(92, _match_winner(79), _match_winner(80), "r16", "right"),
    95: BracketMatchDef(95, _match_winner(86), _match_winner(88), "r16", "right"),
    96: BracketMatchDef(96, _match_winner(85), _match_winner(87), "r16", "right"),
    # QF — adjacent R16 pairs on the same side (top → bottom)
    97: BracketMatchDef(97, _match_winner(89), _match_winner(90), "qf", "left"),
    98: BracketMatchDef(98, _match_winner(93), _match_winner(94), "qf", "left"),
    99: BracketMatchDef(99, _match_winner(91), _match_winner(92), "qf", "right"),
    100: BracketMatchDef(100, _match_winner(95), _match_winner(96), "qf", "right"),
    101: BracketMatchDef(101, _match_winner(97), _match_winner(98), "sf", "left"),
    102: BracketMatchDef(102, _match_winner(99), _match_winner(100), "sf", "right"),
    103: BracketMatchDef(103, _match_loser(101), _match_loser(102), "third_place", "center"),
    104: BracketMatchDef(104, _match_winner(101), _match_winner(102), "final", "center"),
}

# Vertical display order (top → bottom) aligned with FIFA bracket funnel lines
LEFT_R32_ORDER = [74, 77, 73, 75, 83, 84, 81, 82]
RIGHT_R32_ORDER = [76, 78, 79, 80, 86, 88, 85, 87]
LEFT_R16_ORDER = [89, 90, 93, 94]
RIGHT_R16_ORDER = [91, 92, 95, 96]
LEFT_QF_ORDER = [97, 98]
RIGHT_QF_ORDER = [99, 100]
