from __future__ import annotations

import hashlib

from apify_client import ApifyClient
from dotenv import load_dotenv

from bryle.chunking import chunk_text
from bryle.config import Settings
from bryle.store import VectorStore


def _chunk_id(url: str, index: int, text: str) -> str:
    digest = hashlib.sha256(f"{url}:{index}:{text}".encode()).hexdigest()
    return digest[:32]


def main() -> None:
    load_dotenv()
    settings = Settings.from_env(require_apify=True)
    client = ApifyClient(settings.apify_api_token)

    print(f"Crawling {settings.website_url}")
    run = client.actor("apify/website-content-crawler").call(
        run_input={
            "startUrls": [{"url": settings.website_url}],
            "maxCrawlPages": settings.max_crawl_pages,
        }
    )

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        raise RuntimeError("Apify crawl finished without a dataset id.")

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int | float | bool]] = []
    page_count = 0

    for item in client.dataset(dataset_id).iterate_items():
        text = (item.get("text") or "").strip()
        url = (item.get("url") or item.get("loadedUrl") or "").strip()
        title = (item.get("metadata") or {}).get("title") or item.get("title") or ""
        if not text or not url:
            continue

        page_count += 1
        for index, chunk in enumerate(chunk_text(text)):
            ids.append(_chunk_id(url, index, chunk))
            documents.append(chunk)
            metadatas.append(
                {
                    "source": url,
                    "title": str(title),
                    "chunk_index": index,
                }
            )

    if not documents:
        raise RuntimeError("The crawl produced no usable text. Check the target website and Apify run.")

    store = VectorStore(settings)
    store.reset()
    store.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print(f"Indexed {len(documents)} chunks from {page_count} pages into {settings.chroma_path}.")


if __name__ == "__main__":
    main()

