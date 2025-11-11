"""CLI entry point for generating synthetic song lyrics."""

from __future__ import annotations

from lyrics_generation import (
    GenerationConfig,
    SONG_PROMPTS,
    create_lyrics_dataset,
    get_client,
)


def main() -> None:
    client = get_client()
    config = GenerationConfig()
    dataset = create_lyrics_dataset(client, SONG_PROMPTS, config)

    for record in dataset:
        print(f"=== {record['title']} ===")
        print(f"Theme: {record['theme']}")
        print(f"Vibe: {record['vibe']}")
        print("Lyrics:")
        print(record["lyrics"])
        print()

    print(f"Saved {len(dataset)} songs to {config.output_path.resolve()}")


if __name__ == "__main__":
    main()
