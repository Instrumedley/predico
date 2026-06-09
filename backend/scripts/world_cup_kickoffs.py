"""
2026 World Cup group-stage kickoff times from FIFA.com (country=SE schedule).

Each entry mirrors the FIFA fixtures page grouping:
(home_team, away_team, fifa_schedule_date, hour, minute, venue_utc_offset)

Times are parsed with fifa_schedule_time_to_kickoff_utc() — afternoon/evening
values are UTC; early-morning values are Sweden local (CEST). Venue offsets follow
the Wikipedia/FIFA host-city schedule (e.g. Mexico City UTC-6 in June).
"""
from datetime import date

# fmt: off
FIFA_GROUP_STAGE_KICKOFFS = [
    # Group A
    ("Mexico", "S. Africa", date(2026, 6, 11), 19, 0, -6),
    ("South Korea", "Czechia", date(2026, 6, 12), 2, 0, -6),
    ("S. Africa", "Czechia", date(2026, 6, 18), 16, 0, -4),
    ("Mexico", "South Korea", date(2026, 6, 19), 1, 0, -6),
    ("Czechia", "Mexico", date(2026, 6, 25), 1, 0, -6),
    ("S. Africa", "South Korea", date(2026, 6, 25), 1, 0, -6),
    # Group B
    ("Canada", "Bosnia & Herzegovina", date(2026, 6, 12), 19, 0, -4),
    ("Qatar", "Switzerland", date(2026, 6, 13), 19, 0, -7),
    ("Bosnia & Herzegovina", "Switzerland", date(2026, 6, 18), 19, 0, -7),
    ("Canada", "Qatar", date(2026, 6, 18), 22, 0, -7),
    ("Switzerland", "Canada", date(2026, 6, 24), 19, 0, -7),
    ("Bosnia & Herzegovina", "Qatar", date(2026, 6, 24), 19, 0, -7),
    # Group C
    ("Brazil", "Morocco", date(2026, 6, 13), 22, 0, -4),
    ("Haiti", "Scotland", date(2026, 6, 14), 1, 0, -4),
    ("Morocco", "Scotland", date(2026, 6, 19), 22, 0, -4),
    ("Brazil", "Haiti", date(2026, 6, 20), 0, 30, -4),
    ("Scotland", "Brazil", date(2026, 6, 24), 22, 0, -4),
    ("Morocco", "Haiti", date(2026, 6, 24), 22, 0, -4),
    # Group D
    ("United States", "Paraguay", date(2026, 6, 13), 1, 0, -7),
    ("Australia", "Turkey", date(2026, 6, 14), 4, 0, -7),
    ("Paraguay", "Turkey", date(2026, 6, 20), 3, 0, -7),
    ("United States", "Australia", date(2026, 6, 19), 19, 0, -7),
    ("Turkey", "United States", date(2026, 6, 26), 2, 0, -7),
    ("Paraguay", "Australia", date(2026, 6, 26), 2, 0, -7),
    # Group E
    ("Germany", "Curaçao", date(2026, 6, 14), 17, 0, -5),
    ("Ivory Coast", "Ecuador", date(2026, 6, 14), 23, 0, -4),
    ("Curaçao", "Ecuador", date(2026, 6, 21), 0, 0, -5),
    ("Germany", "Ivory Coast", date(2026, 6, 20), 20, 0, -4),
    ("Ecuador", "Germany", date(2026, 6, 25), 20, 0, -4),
    ("Curaçao", "Ivory Coast", date(2026, 6, 25), 20, 0, -4),
    # Group F
    ("Netherlands", "Japan", date(2026, 6, 14), 20, 0, -5),
    ("Sweden", "Tunisia", date(2026, 6, 15), 2, 0, -5),
    ("Japan", "Tunisia", date(2026, 6, 21), 4, 0, -5),
    ("Netherlands", "Sweden", date(2026, 6, 20), 17, 0, -5),
    ("Tunisia", "Netherlands", date(2026, 6, 25), 23, 0, -5),
    ("Japan", "Sweden", date(2026, 6, 25), 23, 0, -5),
    # Group G
    ("Belgium", "Egypt", date(2026, 6, 15), 19, 0, -7),
    ("Iran", "New Zealand", date(2026, 6, 16), 1, 0, -7),
    ("Egypt", "New Zealand", date(2026, 6, 22), 1, 0, -7),
    ("Belgium", "Iran", date(2026, 6, 21), 19, 0, -7),
    ("New Zealand", "Belgium", date(2026, 6, 27), 3, 0, -7),
    ("Egypt", "Iran", date(2026, 6, 27), 3, 0, -7),
    # Group H
    ("Spain", "Cape Verde", date(2026, 6, 15), 16, 0, -4),
    ("Saudi Arabia", "Uruguay", date(2026, 6, 15), 22, 0, -4),
    ("Cape Verde", "Uruguay", date(2026, 6, 21), 22, 0, -4),
    ("Spain", "Saudi Arabia", date(2026, 6, 21), 16, 0, -4),
    ("Uruguay", "Spain", date(2026, 6, 27), 0, 0, -6),
    ("Cape Verde", "Saudi Arabia", date(2026, 6, 27), 0, 0, -5),
    # Group I
    ("France", "Senegal", date(2026, 6, 16), 19, 0, -4),
    ("Iraq", "Norway", date(2026, 6, 16), 22, 0, -4),
    ("Senegal", "Norway", date(2026, 6, 23), 0, 0, -4),
    ("France", "Iraq", date(2026, 6, 22), 21, 0, -4),
    ("Norway", "France", date(2026, 6, 26), 19, 0, -4),
    ("Senegal", "Iraq", date(2026, 6, 26), 19, 0, -4),
    # Group J
    ("Argentina", "Algeria", date(2026, 6, 17), 1, 0, -5),
    ("Austria", "Jordan", date(2026, 6, 17), 4, 0, -7),
    ("Algeria", "Jordan", date(2026, 6, 23), 3, 0, -7),
    ("Argentina", "Austria", date(2026, 6, 22), 17, 0, -5),
    ("Jordan", "Argentina", date(2026, 6, 28), 2, 0, -5),
    ("Algeria", "Austria", date(2026, 6, 28), 2, 0, -5),
    # Group K
    ("Portugal", "DR Congo", date(2026, 6, 17), 17, 0, -5),
    ("Uzbekistan", "Colombia", date(2026, 6, 18), 2, 0, -6),
    ("DR Congo", "Colombia", date(2026, 6, 24), 2, 0, -6),
    ("Portugal", "Uzbekistan", date(2026, 6, 24), 17, 0, -5),
    ("Colombia", "Portugal", date(2026, 6, 27), 23, 30, -4),
    ("DR Congo", "Uzbekistan", date(2026, 6, 27), 23, 30, -4),
    # Group L
    ("England", "Croatia", date(2026, 6, 17), 20, 0, -5),
    ("Ghana", "Panama", date(2026, 6, 17), 23, 0, -4),
    ("Croatia", "Panama", date(2026, 6, 23), 23, 0, -4),
    ("England", "Ghana", date(2026, 6, 23), 20, 0, -4),
    ("Panama", "England", date(2026, 6, 27), 21, 0, -4),
    ("Croatia", "Ghana", date(2026, 6, 27), 21, 0, -4),
]
# fmt: on

assert len(FIFA_GROUP_STAGE_KICKOFFS) == 72
