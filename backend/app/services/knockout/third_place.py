"""Third-place combination matrix lookup for the 2026 World Cup."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.services.knockout.bracket_structure import THIRD_PLACE_WINNER_GROUPS

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "third_place_combinations.json"


@lru_cache(maxsize=1)
def load_third_place_matrix() -> dict[str, dict[str, str]]:
    with DATA_PATH.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def lookup_third_place_assignments(qualifying_third_groups: set[str]) -> dict[str, str] | None:
    """
    Return mapping of winner group letter -> third-place group letter.
    Returns None when fewer than 8 third-place groups are known.
    """
    if len(qualifying_third_groups) != 8:
        return None

    key = "".join(sorted(qualifying_third_groups))
    matrix = load_third_place_matrix()
    return matrix.get(key)


def format_third_place_candidates(groups: tuple[str, ...]) -> str:
    return f"3rd Group {'/'.join(groups)}"


def format_third_place_group(group: str) -> str:
    return f"3rd Group {group}"
