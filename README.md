# Bryle

Bryle is a compact retrieval-augmented generation (RAG) application that crawls a website, indexes its content in Chroma, retrieves relevant passages, and streams source-grounded answers through a FastAPI backend and Next.js frontend.

[Live demo](https://bryle-gules.vercel.app/)

![Bryle homepage](docs/assets/bryle-home.png)

## How it works

1. **Crawl** — Apify extracts pages from a configured website.
2. **Chunk** — page text is split into deterministic overlapping chunks.
3. **Embed** — OpenAI embeddings convert chunks into vectors.
4. **Store** — vectors and source metadata are persisted in Chroma.
5. **Retrieve** — the most relevant chunks are selected for each question.
6. **Generate** — the OpenAI Responses API streams an answer grounded in those chunks.
7. **Cite** — the frontend shows inspectable source cards with supporting snippets.

## Quick start

Python 3.11+ and Node.js 22+ are recommended.

### Backend

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure:

```env
OPENAI_API_KEY=...
APIFY_API_TOKEN=...
WEBSITE_URL=https://example.com
FRONTEND_ORIGINS=http://localhost:3000
```

Build the local knowledge base and start the API:

```bash
python -m scripts.scrape
uvicorn bryle.api:app --reload
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
copy .env.local.example .env.local  # Windows
# cp .env.local.example .env.local  # macOS / Linux
npm run dev
```

Open `http://localhost:3000`.

## Development

```bash
pip install -r requirements-dev.txt
ruff check bryle scripts tests
python -m pytest -q

cd frontend
npm run lint
npm run build
```

## Next steps

- Add hybrid retrieval and reranking for more accurate results.
- Build a small evaluation dataset and track retrieval and answer quality.
- Move ingestion to a background job with deduplication and scheduled refreshes.
- Add observability, authentication, and a hosted vector database for deployment.
