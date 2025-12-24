"""Embed normalized KAMCO documents and upsert them into Qdrant."""

import os

import ollama
from dotenv import load_dotenv
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "kamco")
EMBED_MODEL = os.getenv("EMBED_MODEL", "qwen2.5:latest")

qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
mongo = MongoClient(MONGO_URI)
docs = mongo.kamco.normalized_items


def setup_collection() -> None:
    qdrant.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )


def embed() -> None:
    for doc in docs.find():
        emb = ollama.embeddings(model=EMBED_MODEL, prompt=doc["text"])["embedding"]
        qdrant.upsert(
            collection_name=COLLECTION,
            points=[
                {
                    "id": doc["_id"],
                    "vector": emb,
                    "payload": {"text": doc["text"]},
                }
            ],
        )


if __name__ == "__main__":
    setup_collection()
    embed()
