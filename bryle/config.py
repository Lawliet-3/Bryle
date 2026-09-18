from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigurationError(RuntimeError):
    """Raised when required Bryle configuration is missing or invalid."""


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer, got {raw!r}.") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be greater than zero.")
    return value


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    website_url: str
    apify_api_token: str | None
    chat_model: str
    embedding_model: str
    chroma_path: str
    collection_name: str
    top_k: int
    max_crawl_pages: int

    @classmethod
    def from_env(cls, *, require_apify: bool = False) -> Settings:
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        website_url = os.getenv("WEBSITE_URL", "").strip()
        apify_api_token = os.getenv("APIFY_API_TOKEN", "").strip() or None

        missing: list[str] = []
        if not openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not website_url:
            missing.append("WEBSITE_URL")
        if require_apify and not apify_api_token:
            missing.append("APIFY_API_TOKEN")
        if missing:
            joined = ", ".join(missing)
            raise ConfigurationError(f"Missing required environment variable(s): {joined}")

        return cls(
            openai_api_key=openai_api_key,
            website_url=website_url,
            apify_api_token=apify_api_token,
            chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini").strip(),
            embedding_model=os.getenv(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            ).strip(),
            chroma_path=os.getenv("CHROMA_PATH", ".chroma").strip(),
            collection_name=os.getenv("CHROMA_COLLECTION", "bryle").strip(),
            top_k=_positive_int("TOP_K", 5),
            max_crawl_pages=_positive_int("MAX_CRAWL_PAGES", 50),
        )

