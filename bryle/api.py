from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated, Literal
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAIError
from pydantic import BaseModel, Field

from bryle.config import ConfigurationError, Settings
from bryle.rag import RAGService
from bryle.store import RetrievedChunk

load_dotenv()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12_000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    website: str
    indexed_chunks: int


def _cors_origins() -> list[str]:
    raw = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_service() -> RAGService:
    try:
        return RAGService(Settings.from_env())
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


Service = Annotated[RAGService, Depends(get_service)]


def _snippet(text: str, *, limit: int = 240) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1].rstrip()}…"


def _source_payload(chunks: list[RetrievedChunk]) -> list[dict[str, object]]:
    sources: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, chunk in enumerate(chunks, start=1):
        parsed = urlparse(chunk.source)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or chunk.source in seen
        ):
            continue
        seen.add(chunk.source)
        sources.append(
            {
                "index": index,
                "title": chunk.title or chunk.source,
                "url": chunk.source,
                "snippet": _snippet(chunk.text),
            }
        )
    return sources


def _sse(payload: dict[str, object]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _stream_chat(service: RAGService, request: ChatRequest) -> Iterator[str]:
    chunks = service.retrieve(request.question)
    yield _sse({"type": "sources", "sources": _source_payload(chunks)})

    history = [message.model_dump() for message in request.history[-6:]]
    try:
        for delta in service.stream_answer(
            question=request.question,
            chunks=chunks,
            history=history,
        ):
            yield _sse({"type": "delta", "text": delta})
    except OpenAIError:
        yield _sse(
            {
                "type": "error",
                "message": "The model service is temporarily unavailable. Please try again.",
            }
        )
        return

    yield _sse({"type": "done"})


app = FastAPI(
    title="Bryle API",
    description="Streaming API for the Bryle website RAG assistant.",
    version="2.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse)
def health(service: Service) -> HealthResponse:
    return HealthResponse(
        status="ok",
        website=service.settings.website_url,
        indexed_chunks=service.count(),
    )


@app.post("/api/chat")
def chat(request: ChatRequest, service: Service) -> StreamingResponse:
    return StreamingResponse(
        _stream_chat(service, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
