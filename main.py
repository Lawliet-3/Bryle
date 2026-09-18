from __future__ import annotations

from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

from bryle.config import ConfigurationError, Settings
from bryle.rag import RAGService


load_dotenv()
st.set_page_config(page_title="Bryle", page_icon="🔎", layout="centered")


def _site_name(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or url


@st.cache_resource
def get_service() -> RAGService:
    return RAGService(Settings.from_env())


def render_sources(chunks) -> None:
    seen: set[str] = set()
    sources = []
    for chunk in chunks:
        if chunk.source and chunk.source not in seen:
            seen.add(chunk.source)
            sources.append(chunk)

    if not sources:
        return

    with st.expander(f"Sources ({len(sources)})"):
        for index, chunk in enumerate(sources, start=1):
            label = chunk.title or chunk.source
            st.markdown(f"**[{index}] {label}**")
            st.markdown(chunk.source)


def main() -> None:
    st.title("Bryle")
    st.caption("A small, source-grounded RAG assistant for a website.")

    try:
        service = get_service()
    except ConfigurationError as exc:
        st.error(str(exc))
        st.info("Copy .env.example to .env, fill in the required values, then restart the app.")
        st.stop()

    site = _site_name(service.settings.website_url)

    with st.sidebar:
        st.subheader("Index")
        st.write(f"**Website:** {site}")
        st.write(f"**Indexed chunks:** {service.count()}")
        st.caption("To refresh the knowledge base, run: python -m scripts.scrape")
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        st.info(f"Ask a question about **{site}**. Answers are grounded in the indexed pages.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input(f"Ask about {site}…")
    if not question:
        return

    prior_history = [
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.messages
    ]
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    chunks = service.retrieve(question)
    with st.chat_message("assistant"):
        answer = st.write_stream(
            service.stream_answer(
                question=question,
                chunks=chunks,
                history=prior_history,
            )
        )
        render_sources(chunks)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": chunks,
        }
    )


if __name__ == "__main__":
    main()
