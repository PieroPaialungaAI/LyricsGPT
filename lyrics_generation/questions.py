from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class QuestionEntry:
    song_title: str
    excerpt: str
    question: str
    timestamp: str


def load_questions(path: Path) -> List[Dict[str, str]]:
    """Load stored questions from disk."""

    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def append_question(
    path: Path,
    *,
    song_title: str,
    excerpt: str,
    question: str,
) -> None:
    """Append a question entry to the log."""

    entry = QuestionEntry(
        song_title=song_title,
        excerpt=excerpt.strip(),
        question=question.strip(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    data = load_questions(path)
    data.append(asdict(entry))
    _ensure_parent(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
