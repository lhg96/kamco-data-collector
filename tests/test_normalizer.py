import importlib


def test_normalize_builds_text_and_hash(monkeypatch):
    import normalize.kamco_normalizer as normalizer

    mod = importlib.reload(normalizer)

    class StubRawCol:
        def find(self):
            return [
                {"_id": "A1", "raw": {"pblancNm": "Test", "lctnAddr": "Seoul", "lwsbidPrc": "1000", "pbancBgngYmd": "20240101", "pbancEndYmd": "20240110"}},
            ]

    class StubNormCol:
        def __init__(self):
            self.upserts = []

        def update_one(self, filt, doc, upsert=False):
            self.upserts.append((filt, doc, upsert))

    stub_norm = StubNormCol()

    mod.raw_col = StubRawCol()
    mod.norm_col = stub_norm

    mod.normalize()

    assert len(stub_norm.upserts) == 1
    filt, doc, upsert = stub_norm.upserts[0]
    assert filt["_id"] == "A1"
    assert "공매물건명" in doc["$set"]["text"]
    assert len(doc["$set"]["hash"]) == 64
    assert upsert is True
