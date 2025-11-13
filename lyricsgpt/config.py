from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GenerationConfig:
    """Runtime configuration for lyric generation."""

    model: str = "gpt-4o"
    temperature: float = 0.95
    max_output_tokens: int = 800
    output_path: Path = Path("./data/generated_lyrics.json")
    questions_path: Path = Path("./data/questions.json")
