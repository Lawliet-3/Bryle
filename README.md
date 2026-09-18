# Bryle

Bryle is a compact retrieval-augmented generation (RAG) application that crawls a website, indexes its content in Chroma, retrieves relevant passages for a question, and generates a source-grounded answer in Streamlit.

This repository started as an early LangChain experiment. The current version keeps the original idea but makes the pipeline explicit and easier to understand, test, and extend.

**Live demo:** [brylebot.streamlit.app](https://brylebot.streamlit.app/)

## How it works

1. **Crawl** — Apify extracts pages from a configured website.
2. **Chunk** — page text is split into deterministic overlapping chunks.
3. **Embed** — OpenAI embeddings convert chunks into vectors.
4. **Store** — vectors and source metadata are persisted in Chroma.
5. **Retrieve** — the most relevant chunks are fetched for each question.
6. **Generate** — OpenAI answers using only retrieved context.
7. **Cite** — the UI exposes the source pages used for retrieval.



## Quick start

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set at least:

```env
OPENAI_API_KEY=...
APIFY_API_TOKEN=...
WEBSITE_URL=https://example.com
```

Build the knowledge base:

```bash
python -m scripts.scrape
```

Start the app:

```bash
streamlit run main.py
```

## Development

```bash
pip install -r requirements-dev.txt
ruff check main.py bryle scripts tests
python -m pytest -q
```

GitHub Actions runs the same lint and test checks for pull requests.


## Next steps

- Add hybrid retrieval and reranking for more accurate results.
- Build a small evaluation dataset and track retrieval and answer quality.
- Move ingestion to a background job with deduplication and scheduled refreshes.
- Add observability, authentication, and a hosted vector database for deployment.
