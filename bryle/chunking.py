from __future__ import annotations


def chunk_text(text: str, *, chunk_size: int = 1800, overlap: int = 200) -> list[str]:
    """Split text into readable overlapping chunks without external dependencies."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(cleaned)

    while start < text_length:
        tentative_end = min(start + chunk_size, text_length)
        end = tentative_end

        if tentative_end < text_length:
            lower_bound = start + chunk_size // 2
            newline_break = cleaned.rfind("\n", lower_bound, tentative_end)
            sentence_break = cleaned.rfind(". ", lower_bound, tentative_end)
            best_break = max(newline_break, sentence_break)
            if best_break > start:
                end = best_break + 1

        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= text_length:
            break

        next_start = end - overlap
        start = max(next_start, start + 1)

    return chunks
