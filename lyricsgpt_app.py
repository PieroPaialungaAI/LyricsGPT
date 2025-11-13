from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import streamlit as st

from lyricsgpt import (
    GenerationConfig,
    SONG_PROMPTS,
    answer_question,
    create_lyrics_dataset,
    get_client,
    load_songs_from_json,
)

APP_TITLE = "Use LLM to explore the lyrics of your favorite song"


@st.cache_data(show_spinner=False)
def load_dataset(path: Path) -> List[Dict[str, str]]:
    if path.exists():
        return load_songs_from_json(path)
    return []


def main() -> None:
    st.set_page_config(page_title="LyricsGPT", layout="centered")
    st.title(APP_TITLE)
    st.caption(
        "LyricsGPT lets you explore AI-generated lyrics for a curated set of song "
        "concepts. Provide your OpenAI API key to regenerate lyrics or ask new questions."
    )

    config = GenerationConfig()
    dataset_path = config.output_path

    api_key_input = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help=(
            "Enter your API key to access lyric regeneration and Q&A. Leave blank to "
            "browse previously generated lyrics only."
        ),
    )
    api_key = api_key_input.strip()

    dataset = load_dataset(dataset_path)

    #col_regen, col_status = st.columns([1, 2], gap="large")

    # if regenerate_clicked:
    #     try:
    #         client = get_client(api_key)
    #     except EnvironmentError:
    #         col_status.error("Please provide a valid OpenAI API key.")
    #     else:
    #         with st.spinner("Generating fresh lyrics with OpenAI..."):
    #             dataset = create_lyrics_dataset(client, SONG_PROMPTS, config)
    #         load_dataset.clear()
    #         col_status.success(
    #             f"Generated {len(dataset)} songs and saved to {dataset_path.resolve()}"
    #         )

    #dataset = load_dataset(dataset_path)

    if not dataset:
        st.warning(
            "No lyrics dataset found. Provide an OpenAI API key above and press"
            " 'Regenerate lyrics with LLM' to create one."
        )
        return

    song_titles = [record["title"] for record in dataset]
    selected_title = st.selectbox("Select a song", song_titles)
    selected_song = next(record for record in dataset if record["title"] == selected_title)

    st.markdown(f"## {selected_song['title']}")
    # st.write(f"**Theme:** {selected_song['theme']}")
    # st.write(f"**Vibe:** {selected_song['vibe']}")
    # st.write(f"**Secret twist:** {selected_song['twist']}")

    st.divider()
    st.markdown("### Lyrics")
    st.markdown(selected_song["lyrics"])

    st.divider()
    st.markdown("### Ask a question about a specific excerpt")

    if not api_key:
        st.info("Enter your OpenAI API key above to ask new questions about the lyrics.")
        st.stop()

    st.write(
        "Highlight the relevant lines in the lyrics above, copy them, and paste "
        "into the excerpt box below before submitting your question."
    )

    excerpt = st.text_area(
        "Selected excerpt",
        placeholder="Paste the lyric lines you want to ask about...",
        height=120,
    )
    question = st.text_area(
        "Your question",
        placeholder="What would you like to know about this excerpt?",
        height=120,
    )

    col_submit, col_options = st.columns([1, 2])
    allow_web = col_options.checkbox("Allow supplementary web search", value=True)
    max_results = col_options.slider("Max search results", 1, 5, 3, disabled=not allow_web)

    submit_clicked = col_submit.button("Get answer", disabled=not api_key)
    if submit_clicked:
        if not question.strip():
            st.error("Please enter your question.")
        else:
            client = get_client(api_key)
            with st.spinner("Thinking..."):
                result = answer_question(
                    client,
                    config,
                    song=selected_song,
                    excerpt=excerpt,
                    question=question,
                    allow_web=allow_web,
                    max_search_results=max_results,
                )
            st.subheader("Answer")
            st.markdown(result["answer"])

            if result.get("search_results"):
                st.subheader("Research references")
                for res in result["search_results"]:
                    st.markdown(f"**{res['title']}** — {res['snippet']}")
                    st.markdown(f"[{res['url']}]({res['url']})")
                    st.write("")
            elif result.get("search_error"):
                st.warning(f"Web search failed: {result['search_error']}")

    st.info(f"Dataset source: `{dataset_path}`")


if __name__ == "__main__":
    main()

