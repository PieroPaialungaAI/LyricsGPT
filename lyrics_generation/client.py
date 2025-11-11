from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI


def get_client(api_key: Optional[str] = None) -> OpenAI:
    """Instantiate the OpenAI client using environment configuration."""

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set OPENAI_API_KEY before generating lyrics.")

    return OpenAI(api_key=api_key)
