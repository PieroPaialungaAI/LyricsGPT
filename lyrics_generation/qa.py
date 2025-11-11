from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from .config import GenerationConfig

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://duckduckgo.com/",
}
DUCKDUCKGO_HTML = "https://duckduckgo.com/html/"


def perform_web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Return a list of web search results (title, url, snippet)."""

    response = requests.get(
        DUCKDUCKGO_HTML,
        params={"q": query, "kl": "us-en"},
        headers=REQUEST_HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: List[Dict[str, str]] = []

    for result in soup.select("div.result"):
        link = result.select_one("a.result__a")
        snippet = result.select_one("a.result__snippet, div.result__snippet")
        if not link:
            continue
        url = link.get("href")
        if not url:
            continue
        title = link.get_text(strip=True)
        description = snippet.get_text(strip=True) if snippet else ""
        results.append({"title": title, "url": url, "snippet": description})
        if len(results) >= max_results:
            break

    return results


def _format_search_results(results: Iterable[Dict[str, str]]) -> str:
    formatted = []
    for idx, result in enumerate(results, start=1):
        formatted.append(
            f"Result {idx}: {result['title']}\nURL: {result['url']}\nSnippet: {result['snippet']}"
        )
    return "\n\n".join(formatted) if formatted else "None"


def answer_question(
    client: OpenAI,
    config: GenerationConfig,
    *,
    song: Dict[str, Any],
    excerpt: str,
    question: str,
    allow_web: bool = True,
    max_search_results: int = 3,
) -> Dict[str, Any]:
    """Return an LLM-generated answer with optional web context."""

    search_results: List[Dict[str, str]] = []
    search_error: str | None = None

    if allow_web and question.strip():
        query = f"{song['title']} lyrics {question}" if song.get("title") else question
        try:
            search_results = perform_web_search(query, max_results=max_search_results)
        except Exception as exc:  # pragma: no cover - network issues
            search_error = str(exc)

    external_context = _format_search_results(search_results)
    if search_error:
        external_context = f"Search failed: {search_error}"

    user_prompt = (
        "You are LyricsGPT, an assistant that explains song lyrics.\n"
        "Your answer will go directly to the user, so be helpful, concise and to the point."
        "Use the provided song metadata, excerpt, and any external research to"
        " craft a thoughtful answer. When speculating, say so. If the answer"
        " isn't clear, explain what additional context would help.\n\n"
        "Use the context provided by the question and rely on the web search ONLY WHEN NECESSARY (not because you can)."
        "Song metadata:\n"
        f"- Title: {song.get('title', 'Unknown')}\n"
        f"- Theme: {song.get('theme', 'Unknown')}\n"
        f"- Vibe: {song.get('vibe', 'Unknown')}\n"
        f"- Secret twist: {song.get('twist', 'Unknown')}\n\n"
        "Lyric excerpt:\n"
        f"{excerpt.strip() or 'No excerpt provided.'}\n\n"
        "User question:\n"
        f"{question.strip()}\n\n"
        "External research results:\n"
        f"{external_context}\n\n"
        "Now provide your answer in clear prose."
    )

    response = client.responses.create(
        model=os.getenv("OPENAI_QA_MODEL", config.model),
        temperature=min(config.temperature, 0.7),
        max_output_tokens=min(config.max_output_tokens, 600),
        input=[
            {
                "role": "system",
                "content": (
                    "You are a precise and empathetic lyric analyst. Cite insights"
                    " from the provided excerpt or research snippets when possible."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
    )

    return {
        "answer": response.output_text.strip(),
        "search_results": search_results,
        "search_error": search_error,
    }
