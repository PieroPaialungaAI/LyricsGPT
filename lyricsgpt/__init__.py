"""Utilities for generating and storing synthetic song lyrics."""

from .client import get_client
from .config import GenerationConfig
from .pipeline import create_lyrics_dataset
from .prompts import SONG_PROMPTS, SongPrompt
from .qa import answer_question
from .questions import append_question, load_questions
from .storage import load_songs_from_json, save_songs_to_json

__all__ = [
    "GenerationConfig",
    "SongPrompt",
    "SONG_PROMPTS",
    "answer_question",
    "append_question",
    "create_lyrics_dataset",
    "get_client",
    "load_questions",
    "load_songs_from_json",
    "save_songs_to_json",
]
