import re
import time
from typing import Optional
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup, Comment
from constants import * 


def _resolve_duckduckgo_redirect(url: str) -> Optional[str]:
    """Extract the actual destination URL from DuckDuckGo redirect links."""
    if not url:
        return None
    if url.startswith("https://duckduckgo.com/l/?") or url.startswith("/l/?"):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        redirected = query.get("uddg")
        if redirected:
            return unquote(redirected[0])
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return None


def _duckduckgo_request(url: str, query: str) -> Optional[BeautifulSoup]:
    params = {"q": query, "kl": "us-en"}
    response = requests.get(url, params=params, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        return None
    return BeautifulSoup(response.text, "html.parser")


def search_lyrics_urls(artist: str, title: str, *, max_results: int = 5) -> list[str]:
    """Search DuckDuckGo for potential lyric pages for the song."""
    query = f"{title} {artist} lyrics"

    soups = [
        _duckduckgo_request(DUCKDUCKGO_HTML, query),
        _duckduckgo_request(DUCKDUCKGO_LITE, query),
    ]

    urls: list[str] = []
    for soup in soups:
        if soup is None:
            continue
        links = soup.select("a.result__a") or soup.select("a.result-link")
        for link in links:
            href = _resolve_duckduckgo_redirect(link.get("href"))
            if not href:
                continue
            if any(domain in href for domain in ("azlyrics.com", "lyrics.com", "genius.com")):
                if href not in urls:
                    urls.append(href)
            if len(urls) >= max_results:
                break
        if urls:
            break
    return urls

def build_azlyrics_url(artist: str, title: str) -> str:
    """Construct the AZLyrics URL for the given song."""
    clean = re.compile(r"[^a-z0-9]")
    artist_slug = clean.sub("", artist.lower())
    title_slug = clean.sub("", title.lower())
    return f"https://www.azlyrics.com/lyrics/{artist_slug}/{title_slug}.html"


def fetch_lyrics_from_azlyrics(artist: str, title: str, debug: bool = False) -> Optional[str]:
    """Attempt to fetch lyrics from AZLyrics using the direct URL."""
    url = build_azlyrics_url(artist, title)
    if debug:
        print(f"→ AZLyrics URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as exc:
        if debug:
            print(f"AZLyrics request failed: {exc}")
        return None

    if response.status_code != 200:
        if debug:
            print(f"AZLyrics returned status {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    comment = soup.find(
        string=lambda text: isinstance(text, Comment)
        and "Usage of azlyrics.com content" in text
    )
    if not comment:
        if debug:
            print("AZLyrics marker comment not found")
        return None

    lyrics_div = comment.find_next_sibling("div")
    if not lyrics_div:
        if debug:
            print("AZLyrics lyrics div missing")
        return None

    lyrics = lyrics_div.get_text(separator="\n").strip()
    if debug and lyrics:
        print("AZLyrics lyric snippet:")
        for line in lyrics.splitlines()[:3]:
            print(f"  {line}")
    return lyrics or None


def fetch_lyrics_from_url(url: str) -> Optional[str]:
    """Fetch lyrics by scraping a known lyrics website."""
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    if "lyrics.com" in url:
        lyric_box = soup.find("pre", id="lyric-body-text")
        if lyric_box:
            return lyric_box.get_text(separator="\n").strip()

    if "genius.com" in url:
        containers = soup.select('div[data-lyrics-container="true"]')
        if containers:
            return "\n".join(
                container.get_text(separator="\n").strip()
                for container in containers
            ).strip()

    if "azlyrics.com" in url:
        comment = soup.find(
            string=lambda text: isinstance(text, Comment)
            and "Usage of azlyrics.com content" in text
        )
        if comment:
            lyrics_div = comment.find_next_sibling("div")
            if lyrics_div:
                return lyrics_div.get_text(separator="\n").strip()

    return None


def scrape_lyrics(
    artist: str,
    title: str,
    *,
    delay: float = 1.0,
    debug: bool = False,
) -> Optional[str]:
    """Fetch lyrics by trying direct AZLyrics URL first, then search results."""
    if debug:
        print(f"Trying AZLyrics direct URL for {artist!r} - {title!r}")
    lyrics = fetch_lyrics_from_azlyrics(artist, title, debug=debug)
    if lyrics:
        if debug:
            print("✓ Found via AZLyrics direct URL")
        return lyrics

    if debug:
        print("AZLyrics direct lookup failed; searching DuckDuckGo...")
    urls = search_lyrics_urls(artist, title)
    if debug:
        print(f"Candidate URLs: {urls}")
    for url in urls:
        if debug:
            print(f"→ Fetching {url}")
        time.sleep(delay)  # be polite and avoid hammering sites
        lyrics = fetch_lyrics_from_url(url)
        if lyrics:
            if debug:
                print("✓ Lyrics retrieved from result")
            return lyrics
    if debug:
        print("No lyrics found in search results")
    return None
