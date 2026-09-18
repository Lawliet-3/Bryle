import pytest

from bryle.chunking import chunk_text


def test_chunk_text_returns_empty_for_whitespace() -> None:
    assert chunk_text("  \n  ") == []


def test_chunk_text_splits_long_text_with_overlap() -> None:
    text = " ".join(f"sentence-{i}." for i in range(200))
    chunks = chunk_text(text, chunk_size=300, overlap=40)

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    assert all(len(chunk) <= 300 for chunk in chunks)


def test_chunk_text_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=100)
