from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Dict


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_songs_to_json(records: Iterable[dict[str, str]], path: Path) -> None:
    """Persist generated lyrics to a JSON file."""

    data = list(records)
    _ensure_parent(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_songs_from_json(path: Path) -> List[Dict[str, str]]:
    """Load previously generated lyrics from a JSON file."""

    if not path.exists():
        raise FileNotFoundError(f"Lyrics dataset not found at {path}")

    return json.loads(path.read_text(encoding="utf-8"))
