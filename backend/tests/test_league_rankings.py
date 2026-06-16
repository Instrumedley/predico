"""Tests for league ranking order and tie-break rules."""
from app.services.league_service import assign_league_ranks


def test_assign_league_ranks_breaks_ties_on_perfect_predictions():
    rows = [
        (1, "alice", 600, 5),
        (2, "bob", 600, 3),
        (3, "carol", 400, 10),
    ]

    ranked = assign_league_ranks(rows)

    assert [entry[0] for entry in ranked] == [1, 2, 3]
    assert ranked[0][1:] == (1, "alice", 600, 5)
    assert ranked[1][1:] == (2, "bob", 600, 3)


def test_assign_league_ranks_shares_rank_when_fully_tied():
    rows = [
        (1, "alice", 600, 5),
        (2, "bob", 600, 5),
        (3, "carol", 400, 0),
    ]

    ranked = assign_league_ranks(rows)

    assert ranked[0][0] == 1
    assert ranked[1][0] == 1
    assert ranked[2][0] == 3
