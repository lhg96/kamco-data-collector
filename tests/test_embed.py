import importlib


def test_setup_collection(monkeypatch):
    import rag.embed as embed

    mod = importlib.reload(embed)

    called = {}

    class StubQdrant:
        def recreate_collection(self, collection_name, vectors_config):
            called["collection_name"] = collection_name
            called["vectors_config"] = vectors_config

    mod.qdrant = StubQdrant()
    mod.setup_collection()

    assert called["collection_name"] == mod.COLLECTION
    assert getattr(called["vectors_config"], "size", 768) == 768


def test_embed_upserts(monkeypatch):
    import rag.embed as embed

    mod = importlib.reload(embed)

    class StubDocs:
        def find(self):
            return [{"_id": "A1", "text": "hello world"}]

    class StubQdrant:
        def __init__(self):
            self.upserts = []

        def upsert(self, collection_name, points):
            self.upserts.append((collection_name, points))

    class StubOllama:
        def embeddings(self, model, prompt):
            return {"embedding": [0.0] * 768}

    stub_qdrant = StubQdrant()
    mod.qdrant = stub_qdrant
    mod.docs = StubDocs()
    mod.ollama = StubOllama()

    mod.embed()

    assert len(stub_qdrant.upserts) == 1
    collection_name, points = stub_qdrant.upserts[0]
    assert collection_name == mod.COLLECTION
    assert points[0]["id"] == "A1"
    assert len(points[0]["vector"]) == 768
