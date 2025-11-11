from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SongPrompt:
    """Template metadata for generating a single song."""

    title: str
    theme: str
    vibe: str
    twist: str

    def format_prompt(self) -> str:
        return (
            f"Write full song lyrics titled '{self.title}'.\n"
            f"Theme: {self.theme}. Vibe: {self.vibe}.\n"
            "Blend a catchy chorus, vivid storytelling verses, and a bridge that"
            " adds a cryptic clue. Keep it under ~250 words, structured with"
            " labeled sections (Verse/Chorus/Bridge/Outro). Include contemporary"
            " imagery and clever hooks reminiscent of Taylor Swift, Ed Sheeran,"
            " and Olivia Rodrigo, without copying existing songs."
            f" Secret twist to weave in: {self.twist}."
        )


SONG_PROMPTS: List[SongPrompt] = [
    SongPrompt(
        title="Glitter in the Rearview",
        theme="letting go of a high-profile love story",
        vibe="late-night highway pop ballad",
        twist="a hidden reference to a fleet number 13",
    ),
    SongPrompt(
        title="Static Bouquet",
        theme="finding romance through fuzzy radio signals",
        vibe="folktronica confession",
        twist="use Morse code imagery without writing actual code",
    ),
    SongPrompt(
        title="Velvet Algorithm",
        theme="love decoded by mathematical metaphors",
        vibe="sleek synth pop",
        twist="a password no one else can hack",
    ),
    SongPrompt(
        title="Parachutes of Honey",
        theme="falling for someone who slows down time",
        vibe="acoustic daydream",
        twist="gravity becomes a sweet addiction",
    ),
    SongPrompt(
        title="Paper Planets",
        theme="long-distance lovers mapping constellations",
        vibe="cinematic indie ballad",
        twist="postcards that orbit in sync",
    ),
    SongPrompt(
        title="Silver Tongue Graffiti",
        theme="graffiti artists writing their history",
        vibe="percussive pop-rap hybrid",
        twist="a coded message sprayed at 2:17 AM",
    ),
    SongPrompt(
        title="Mint Condition Ghosts",
        theme="collecting memories like rare vinyl",
        vibe="nostalgic dream pop",
        twist="side B hides the secret track",
    ),
    SongPrompt(
        title="Crimson Parallax",
        theme="love across parallel timelines",
        vibe="dark electro ballad",
        twist="an eclipse that runs backwards",
    ),
    SongPrompt(
        title="Hologram Garden",
        theme="digital intimacy blooming in augmented reality",
        vibe="airy alt-R&B",
        twist="flowers made of cached pixels",
    ),
    SongPrompt(
        title="Summer Ink in October",
        theme="rebellious romance replayed when seasons collide",
        vibe="storytelling folk-pop",
        twist="a journal entry on page 108 that predicts the future",
    ),
]
