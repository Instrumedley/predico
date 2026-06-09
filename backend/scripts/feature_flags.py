"""
Toggle backend feature flags in local .env and print Heroku commands for production.

Usage (local — updates backend/.env):
  python scripts/feature_flags.py league-progress-chart on
  python scripts/feature_flags.py league-progress-chart off
  python scripts/feature_flags.py league-progress-chart status

Usage (Heroku — prints the command to run):
  python scripts/feature_flags.py league-progress-chart on --heroku predico-api
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_ROOT / ".env"

FLAGS = {
    "league-progress-chart": "LEAGUE_PROGRESS_CHART_ENABLED",
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Toggle Predico backend feature flags.")
    parser.add_argument(
        "flag",
        choices=sorted(FLAGS.keys()),
        help="Feature flag to manage",
    )
    parser.add_argument(
        "state",
        choices=["on", "off", "status"],
        help="Enable, disable, or show current local value",
    )
    parser.add_argument(
        "--heroku",
        metavar="APP_NAME",
        help="Print heroku config:set command instead of editing local .env",
    )
    args = parser.parse_args()

    env_key = FLAGS[args.flag]

    if args.state == "status":
        current = get_flag(env_key)
        if current is None:
            print(f"{env_key} is not set in {ENV_FILE} (defaults to false).")
        else:
            print(f"{env_key}={current}")
        return 0

    enabled = args.state == "on"
    value = "true" if enabled else "false"

    if args.heroku:
        print(f'heroku config:set {env_key}={value} -a {args.heroku}')
        print("Restart is not required; the dyno picks up config on next request.")
        return 0

    set_flag(env_key, enabled)
    print(f"Updated {ENV_FILE}: {env_key}={value}")
    print("Restart the backend container/process to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
