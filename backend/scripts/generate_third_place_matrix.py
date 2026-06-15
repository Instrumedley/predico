"""Generate third_place_combinations.json from Wikipedia knockout stage table."""
import json
import re
from pathlib import Path

WINNER_COLS = ["A", "B", "D", "E", "G", "I", "K", "L"]
ROW_PATTERN = re.compile(
    r"\|\s*\d+\s*\|\s*([A-L](?:\s*\|\s*[A-L]){7})\s*\|\s*((?:3[A-L]\s*\|\s*){7}3[A-L])\s*\|"
)


def parse_table(text: str) -> dict[str, dict[str, str]]:
    combos: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        match = ROW_PATTERN.match(line)
        if not match:
            continue
        groups = [part.strip() for part in match.group(1).split("|")]
        thirds = [part.strip().replace("3", "") for part in match.group(2).split("|")]
        key = "".join(sorted(groups))
        combos[key] = dict(zip(WINNER_COLS, thirds, strict=True))
    return combos


def main() -> None:
    source = Path(__file__).resolve().parents[1] / "app" / "data" / "third_place_combinations_source.txt"
    if not source.exists():
        source = Path(__file__).resolve().parents[1] / "app" / "data" / "third_place_combinations.json"
        if source.exists():
            print(f"JSON already exists at {source}")
            return
        raise SystemExit(f"Source file not found: {source}")

    combos = parse_table(source.read_text(encoding="utf-8"))
    if len(combos) != 495:
        raise SystemExit(f"Expected 495 combinations, got {len(combos)}")

    output = Path(__file__).resolve().parents[1] / "app" / "data" / "third_place_combinations.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(combos, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(combos)} combinations to {output}")


if __name__ == "__main__":
    main()
