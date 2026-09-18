from bryle.rag import format_context
from bryle.store import RetrievedChunk


def test_format_context_numbers_sources() -> None:
    chunks = [
        RetrievedChunk(text="Alpha", source="https://example.com/a", title="A"),
        RetrievedChunk(text="Beta", source="https://example.com/b", title="B"),
    ]

    context = format_context(chunks)

    assert "[1] A" in context
    assert "https://example.com/a" in context
    assert "[2] B" in context
    assert "Beta" in context
