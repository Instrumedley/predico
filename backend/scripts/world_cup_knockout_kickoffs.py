"""
2026 FIFA World Cup knockout kickoff times (matches 73–104).

Times from Wikipedia knockout stage schedule (venue-local wall clock + UTC offset).
"""

from __future__ import annotations

from datetime import date

# (match_number, match_date, hour, minute, venue_utc_offset_hours)
KNOCKOUT_KICKOFFS: list[tuple[int, date, int, int, int]] = [
    # Round of 32
    (73, date(2026, 6, 28), 12, 0, -7),
    (76, date(2026, 6, 29), 12, 0, -5),
    (74, date(2026, 6, 29), 16, 30, -4),
    (75, date(2026, 6, 29), 19, 0, -6),
    (78, date(2026, 6, 30), 12, 0, -5),
    (77, date(2026, 6, 30), 17, 0, -4),
    (79, date(2026, 6, 30), 19, 0, -6),
    (80, date(2026, 7, 1), 12, 0, -4),
    (82, date(2026, 7, 1), 13, 0, -7),
    (81, date(2026, 7, 1), 17, 0, -7),
    (84, date(2026, 7, 2), 12, 0, -7),
    (83, date(2026, 7, 2), 19, 0, -4),
    (85, date(2026, 7, 2), 20, 0, -7),
    (88, date(2026, 7, 3), 13, 0, -5),
    (86, date(2026, 7, 3), 18, 0, -4),
    (87, date(2026, 7, 3), 20, 30, -5),
    # Round of 16
    (90, date(2026, 7, 4), 12, 0, -5),
    (89, date(2026, 7, 4), 17, 0, -4),
    (91, date(2026, 7, 5), 16, 0, -4),
    (92, date(2026, 7, 5), 18, 0, -6),
    (93, date(2026, 7, 6), 14, 0, -5),
    (94, date(2026, 7, 6), 17, 0, -7),
    (95, date(2026, 7, 7), 12, 0, -4),
    (96, date(2026, 7, 7), 13, 0, -7),
    # Quarterfinals
    (97, date(2026, 7, 9), 16, 0, -4),
    (98, date(2026, 7, 10), 12, 0, -7),
    (99, date(2026, 7, 11), 17, 0, -4),
    (100, date(2026, 7, 11), 20, 0, -5),
    # Semifinals
    (101, date(2026, 7, 14), 14, 0, -5),
    (102, date(2026, 7, 15), 15, 0, -4),
    # Third place & Final
    (103, date(2026, 7, 18), 17, 0, -4),
    (104, date(2026, 7, 19), 15, 0, -4),
]

KNOCKOUT_KICKOFFS_BY_MATCH: dict[int, tuple[date, int, int, int]] = {
    match_number: (match_date, hour, minute, offset)
    for match_number, match_date, hour, minute, offset in KNOCKOUT_KICKOFFS
}
