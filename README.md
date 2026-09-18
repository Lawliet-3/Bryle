# Bryle

Bryle is a compact retrieval-augmented generation (RAG) application that crawls a website, indexes its content in Chroma, retrieves relevant passages for a question, and generates a source-grounded answer in Streamlit.

This repository started as an early LangChain experiment. The current version keeps the original idea but makes the pipeline explicit and easier to understand, test, and extend.

## How it works

1. **Crawl** — Apify extracts pages from a configured website.
2. **Chunk** — page text is split into deterministic overlapping chunks.
3. **Embed** — OpenAI embeddings convert chunks into vectors.
4. **Store** — vectors and source metadata are persisted in Chroma.
5. **Retrieve** — the most relevant chunks are fetched for each question.
6. **Generate** — OpenAI answers using only retrieved context.
7. **Cite** — the UI exposes the source pages used for retrieval.

## Architecture

```text
Website
   |
   v
Apify crawler -> chunking -> OpenAI embeddings -> Chroma
                                                |
User question -> query embedding -> retrieval --+
                              |
                              v
                   grounded prompt + history
                              |
                              v
                       OpenAI response
                              |
                              v
                   Streamlit answer + sources
```

## Project structure

```text
.
├── bryle/
│   ├── chunking.py      # deterministic text chunking
│   ├── config.py        # environment configuration
│   ├── rag.py           # retrieval + grounded generation
│   └── store.py         # OpenAI embeddings + Chroma access
├── scripts/
│   └── scrape.py        # crawl and rebuild the local index
├── tests/
├── main.py              # Streamlit application
├── requirements.txt
└── requirements-dev.txt
```

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
pytest -q
```

GitHub Actions runs the same lint and test checks for pull requests.

## Why the rewrite?

- **No LangChain dependency.** The retrieval and generation stages are visible instead of hidden behind chain abstractions.
- **Source-grounded answers.** Retrieved chunks keep page URLs and titles so answers can be traced back to source pages.
- **Prompt-injection awareness.** Crawled website text is explicitly treated as untrusted data rather than executable instructions.
- **Configuration instead of hard-coding.** Models, retrieval depth, crawl limits, collection name, and storage path are environment-driven.
- **Tests and CI.** The repository now has unit tests, linting, and a pull-request workflow.

## Current scope

Bryle is intentionally small rather than pretending to be a production platform. Natural next steps are reranking or hybrid retrieval, evaluation datasets, retrieval metrics, ingestion deduplication, observability, background indexing, authentication, and a hosted vector database.

## Original demo

An older Streamlit deployment may still exist at https://brylebot.streamlit.app/, but it was built from the original implementation and may not reflect this version.
