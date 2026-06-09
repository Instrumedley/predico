"""
Print kickoff audit for all FIFA group-stage fixtures.

Shows venue-local time, UTC kickoff, and Sweden display (CEST) for each match.
Run after changing world_cup_kickoffs.py or conversion logic.

Usage:
    python -m scripts.audit_match_times
"""
from datetime import timedelta

from app.utils.match_time import (
    fifa_schedule_time_to_kickoff_utc,
    parse_timezone_offset,
    utc_to_venue_local,
)
from scripts.world_cup_kickoffs import FIFA_GROUP_STAGE_KICKOFFS

SWEDEN_OFFSET = 2


def main() -> None:
    print(f"{'Match':<45} {'Venue local':<22} {'UTC kickoff':<18} {'Sweden (CEST)'}")
    print("-" * 110)

    for home, away, schedule_date, hour, minute, venue_offset in FIFA_GROUP_STAGE_KICKOFFS:
        kickoff_utc = fifa_schedule_time_to_kickoff_utc(schedule_date, hour, minute)
        match_time, timezone = utc_to_venue_local(kickoff_utc, venue_offset)
        venue_local = kickoff_utc + timedelta(hours=parse_timezone_offset(timezone))
        sweden_local = kickoff_utc + timedelta(hours=SWEDEN_OFFSET)

        label = f"{home} vs {away}"
        venue_str = f"{venue_local.date()} {match_time} {timezone}"
        utc_str = kickoff_utc.strftime("%Y-%m-%d %H:%M")
        sweden_str = sweden_local.strftime("%Y-%m-%d %H:%M")

        print(f"{label:<45} {venue_str:<22} {utc_str:<18} {sweden_str}")


if __name__ == "__main__":
    main()
