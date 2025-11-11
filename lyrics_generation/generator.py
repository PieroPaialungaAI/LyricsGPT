from __future__ import annotations

import os
from typing import Iterable

from openai import OpenAI

from .config import GenerationConfig
from .prompts import SongPrompt


def generate_lyrics(client: OpenAI, prompt: SongPrompt, config: GenerationConfig) -> str:
    """Generate lyrics for a single prompt using the provided OpenAI client."""

    response = client.responses.create(
        model=os.getenv("OPENAI_LYRICS_MODEL", config.model),
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a platinum-selling songwriter blending poetic imagery,"
                    " irresistible hooks, and subtle puzzles."
                ),
            },
            {"role": "user", "content": prompt.format_prompt()},
        ],
    )
    return response.output_text.strip()


def generate_batch(
    client: OpenAI,
    prompts: Iterable[SongPrompt],
    config: GenerationConfig,
) -> list[dict[str, str]]:
    """Generate lyrics for a collection of prompts and return structured records."""

    songs: list[dict[str, str]] = []
    for prompt in prompts:
        lyrics = generate_lyrics(client, prompt, config)
        songs.append(
            {
                "title": prompt.title,
                "theme": prompt.theme,
                "vibe": prompt.vibe,
                "twist": prompt.twist,
                "lyrics": lyrics,
            }
        )
    return songs
