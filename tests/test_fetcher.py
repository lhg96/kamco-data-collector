import importlib

import pytest


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_fetch_requires_api_key(monkeypatch):
    monkeypatch.delenv("KAMCO_API_KEY", raising=False)
    import collector.kamco_fetcher as fetcher

    mod = importlib.reload(fetcher)
    with pytest.raises(RuntimeError):
        mod.fetch_kamco(page=1, per_page=1)


def test_run_stores_items(monkeypatch):
    monkeypatch.setenv("KAMCO_API_KEY", "fake-key")
    import collector.kamco_fetcher as fetcher

    mod = importlib.reload(fetcher)

    pages = [
        {"data": [{"pblancNo": "A1", "lctnAddr": "Seoul"}, {"pblancNo": "A2"}]},
        {"data": []},
    ]

    class StubSession:
        def __init__(self, payloads):
            self.payloads = payloads
            self.calls = 0

        def get(self, url, params, timeout):
            payload = self.payloads[self.calls]
            self.calls += 1
            return DummyResponse(payload)

    class StubCol:
        def __init__(self):
            self.upserts = []

        def update_one(self, filt, doc, upsert=False):
            self.upserts.append((filt, doc, upsert))

    stub_col = StubCol()
    mod.raw_col = stub_col
    mod.session = StubSession(pages)

    mod.run()

    assert len(stub_col.upserts) == 2
    ids = [filt["_id"] for filt, _, _ in stub_col.upserts]
    assert ids == ["A1", "A2"]
