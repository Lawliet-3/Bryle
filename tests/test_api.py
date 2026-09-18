import json

from fastapi.testclient import TestClient

from bryle.api import app, get_service
from bryle.store import RetrievedChunk


class FakeService:
    def retrieve(self, question: str) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                text="A supporting passage with useful details.",
                source="https://example.com/guide",
                title="Example guide",
            )
        ]

    def stream_answer(self, **_kwargs):
        yield "Grounded "
        yield "answer [1]."


def test_chat_streams_sources_and_answer() -> None:
    app.dependency_overrides[get_service] = lambda: FakeService()
    client = TestClient(app)

    response = client.post("/api/chat", json={"question": "What is Bryle?"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert events[0]["type"] == "sources"
    assert events[0]["sources"][0]["title"] == "Example guide"
    assert "".join(event.get("text", "") for event in events) == "Grounded answer [1]."
    assert events[-1]["type"] == "done"


def test_chat_rejects_blank_questions() -> None:
    app.dependency_overrides[get_service] = lambda: FakeService()
    response = TestClient(app).post("/api/chat", json={"question": ""})

    app.dependency_overrides.clear()
    assert response.status_code == 422
