from __future__ import annotations

from typing import Iterable

from openai import OpenAI

from .config import GenerationConfig
from .generator import generate_batch
from .prompts import SongPrompt
from .storage import save_songs_to_json


def create_lyrics_dataset(
    client: OpenAI,
    prompts: Iterable[SongPrompt],
    config: GenerationConfig,
    *,
    persist: bool = True,
) -> list[dict[str, str]]:
    """Generate lyrics for prompts and optionally persist the dataset."""

    dataset = generate_batch(client, prompts, config)
    if persist:
        save_songs_to_json(dataset, config.output_path)
    return dataset
