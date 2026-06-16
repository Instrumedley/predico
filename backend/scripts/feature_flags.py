"""
Toggle backend feature flags in local .env and print Heroku commands for production.

Usage (local — updates backend/.env):
  python scripts/feature_flags.py league-progress-chart on
  python scripts/feature_flags.py league-progress-chart off
  python scripts/feature_flags.py league-progress-chart status

  python scripts/feature_flags.py knockout-stage on
  python scripts/feature_flags.py knockout-stage on --default true
  python scripts/feature_flags.py knockout-stage on --default false
  python scripts/feature_flags.py knockout-stage off
  python scripts/feature_flags.py knockout-stage status

  python scripts/feature_flags.py dashboard-news-banner on
  python scripts/feature_flags.py dashboard-news-banner off
  python scripts/feature_flags.py dashboard-news-banner status

Usage (Heroku — prints the command to run):
  python scripts/feature_flags.py league-progress-chart on --heroku predico-api
  python scripts/feature_flags.py knockout-stage on --default true --heroku predico-api
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_ROOT / ".env"

FLAG_DEFINITIONS = {
    "league-progress-chart": {
        "enabled": "LEAGUE_PROGRESS_CHART_ENABLED",
    },
    "knockout-stage": {
        "enabled": "KNOCKOUT_STAGE_ENABLED",
        "default": "KNOCKOUT_STAGE_DEFAULT",
    },
    "dashboard-news-banner": {
        "enabled": "DASHBOARD_NEWS_BANNER_ENABLED",
    },
}


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "on", "yes", "enable", "enabled"}:
        return True
    if normalized in {"0", "false", "off", "no", "disable", "disabled"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def _read_env_lines() -> list[str]:
    if not ENV_FILE.exists():
        return []
    return ENV_FILE.read_text(encoding="utf-8").splitlines()


def _write_env_lines(lines: list[str]) -> None:
    ENV_FILE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def set_flag(key: str, enabled: bool) -> None:
    value = "true" if enabled else "false"
    lines = _read_env_lines()
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
    updated = False
    new_lines: list[str] = []

    for line in lines:
        if pattern.match(line):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.append(f"# Feature flags")
        new_lines.append(f"{key}={value}")

    _write_env_lines(new_lines)


def get_flag(key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.*)\s*$")
    for line in _read_env_lines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip().strip('"').strip("'")
    return None


def _print_status(flag_name: str) -> int:
    definition = FLAG_DEFINITIONS[flag_name]
    enabled_key = definition["enabled"]
    enabled_value = get_flag(enabled_key)

    if enabled_value is None:
        print(f"{enabled_key} is not set in {ENV_FILE} (defaults to false).")
    else:
        print(f"{enabled_key}={enabled_value}")

    default_key = definition.get("default")
    if default_key:
        default_value = get_flag(default_key)
        if default_value is None:
            print(f"{default_key} is not set in {ENV_FILE} (defaults to false).")
        else:
            print(f"{default_key}={default_value}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Toggle Predico backend feature flags.")
    parser.add_argument(
        "flag",
        choices=sorted(FLAG_DEFINITIONS.keys()),
        help="Feature flag to manage",
    )
    parser.add_argument(
        "state",
        choices=["on", "off", "status"],
        help="Enable, disable, or show current local value",
    )
    parser.add_argument(
        "--default",
        type=_parse_bool,
        dest="default_view",
        help='For knockout-stage: default dashboard tab when enabled (true=knockout, false=group).',
    )
    parser.add_argument(
        "--heroku",
        metavar="APP_NAME",
        help="Print heroku config:set command instead of editing local .env",
    )
    args = parser.parse_args()

    definition = FLAG_DEFINITIONS[args.flag]
    enabled_key = definition["enabled"]
    default_key = definition.get("default")

    if args.state == "status":
        return _print_status(args.flag)

    enabled = args.state == "on"
    enabled_value = "true" if enabled else "false"

    if args.heroku:
        parts = [f"{enabled_key}={enabled_value}"]
        if enabled and default_key and args.default_view is not None:
            parts.append(f"{default_key}={'true' if args.default_view else 'false'}")
        elif enabled and default_key and args.default_view is None:
            current_default = get_flag(default_key)
            if current_default is not None:
                parts.append(f"{default_key}={current_default}")
        print(f"heroku config:set {' '.join(parts)} -a {args.heroku}")
        print("Restart is not required; the dyno picks up config on next request.")
        return 0

    if args.state == "off":
        set_flag(enabled_key, False)
        print(f"Updated {ENV_FILE}: {enabled_key}=false")
        print("Restart the backend container/process to apply.")
        return 0

    set_flag(enabled_key, True)
    messages = [f"{enabled_key}=true"]

    if default_key:
        if args.default_view is not None:
            set_flag(default_key, args.default_view)
            messages.append(f"{default_key}={'true' if args.default_view else 'false'}")
        else:
            current_default = get_flag(default_key)
            if current_default is None:
                set_flag(default_key, False)
                messages.append(f"{default_key}=false")

    print(f"Updated {ENV_FILE}: {', '.join(messages)}")
    print("Restart the backend container/process to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
