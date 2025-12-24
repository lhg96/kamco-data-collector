"""Normalize raw KAMCO items into text suitable for embedding."""

import hashlib
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

mongo = MongoClient(MONGO_URI)
db = mongo.kamco
raw_col = db.raw_items
norm_col = db.normalized_items


def _build_text(item: dict) -> str:
    return f"""
    공매물건명: {item.get('pblancNm')}
    소재지: {item.get('lctnAddr')}
    최저입찰가: {item.get('lwsbidPrc')}
    입찰기간: {item.get('pbancBgngYmd')} ~ {item.get('pbancEndYmd')}
    """.strip()


def normalize() -> None:
    for doc in raw_col.find():
        item = doc.get("raw", {})
        text = _build_text(item)
        norm_col.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "text": text,
                    "hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                }
            },
            upsert=True,
        )


if __name__ == "__main__":
    normalize()
