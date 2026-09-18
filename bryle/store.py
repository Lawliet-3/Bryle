from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import chromadb
from openai import OpenAI

from bryle.config import Settings


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    title: str | None = None
    distance: float | None = None


class VectorStore:
    """Thin wrapper around Chroma so retrieval behavior stays easy to inspect."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.openai = OpenAI(api_key=settings.openai_api_key)
        self.chroma = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.chroma.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        try:
            self.chroma.delete_collection(self.settings.collection_name)
        except Exception:
            # Chroma raises when the collection does not yet exist.
            pass
        self.collection = self.chroma.get_or_create_collection(
            name=self.settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.openai.embeddings.create(
            model=self.settings.embedding_model,
            input=list(texts),
        )
        return [item.embedding for item in response.data]

    def upsert(
        self,
        *,
        ids: Sequence[str],
        documents: Sequence[str],
        metadatas: Sequence[dict[str, str | int | float | bool]],
        batch_size: int = 100,
    ) -> None:
        if not (len(ids) == len(documents) == len(metadatas)):
            raise ValueError("ids, documents, and metadatas must have equal length")

        for start in range(0, len(documents), batch_size):
            end = start + batch_size
            batch_documents = list(documents[start:end])
            self.collection.upsert(
                ids=list(ids[start:end]),
                documents=batch_documents,
                metadatas=list(metadatas[start:end]),
                embeddings=self._embed(batch_documents),
            )

    def query(self, text: str, *, top_k: int | None = None) -> list[RetrievedChunk]:
        total = self.count()
        if total == 0:
            return []

        n_results = min(top_k or self.settings.top_k, total)
        query_embedding = self._embed([text])[0]
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        chunks: list[RetrievedChunk] = []
        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            distance = distances[index] if index < len(distances) else None
            chunks.append(
                RetrievedChunk(
                    text=document or "",
                    source=str((metadata or {}).get("source", "unknown")),
                    title=(metadata or {}).get("title"),
                    distance=float(distance) if distance is not None else None,
                )
            )
        return chunks
