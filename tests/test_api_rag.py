import importlib

from fastapi.testclient import TestClient


def test_health_and_ask(monkeypatch):
    import api.main as main

    mod = importlib.reload(main)

    class StubHit:
        def __init__(self, text):
            self.payload = {"text": text}

    class StubQdrant:
        def search(self, collection_name, query_vector, limit):
            return [StubHit("context 1"), StubHit("context 2")]

    class StubOllama:
        def embeddings(self, model, prompt):
            return {"embedding": [0.0] * 768}

        def generate(self, model, prompt):
            return {"response": "answer text"}

    mod.qdrant = StubQdrant()
    mod.ollama = StubOllama()

    client = TestClient(mod.app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    res = client.get("/ask", params={"q": "테스트"})
    assert res.status_code == 200
    data = res.json()
    assert data["answer"] == "answer text"
    assert data["matches"] == 2
