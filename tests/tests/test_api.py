import os
os.environ.setdefault("GROQ_API_KEY", "test-key")

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_ok(monkeypatch):
    monkeypatch.setattr(main, "run_agent", lambda m, s: {"answer": "hi", "tools_used": []})
    r = client.post("/chat", json={"message": "hello", "session_id": "t1"})
    assert r.status_code == 200
    assert r.json()["answer"] == "hi"


def test_chat_empty_message_rejected():
    assert client.post("/chat", json={"message": ""}).status_code == 422


def test_chat_agent_failure(monkeypatch):
    def boom(message, session_id):
        raise RuntimeError("fail")
    monkeypatch.setattr(main, "run_agent", boom)
    assert client.post("/chat", json={"message": "hi"}).status_code == 502