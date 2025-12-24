"""FastAPI entrypoint for KAMCO RAG querying."""

import os

import ollama
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "kamco")
GEN_MODEL = os.getenv("GEN_MODEL", "qwen2.5:latest")

app = FastAPI(title="KAMCO RAG API")
qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ask")
def ask(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query is empty.")

    emb = ollama.embeddings(model=GEN_MODEL, prompt=q)["embedding"]

    hits = qdrant.search(
        collection_name=COLLECTION,
        query_vector=emb,
        limit=5,
    )

    context = "\n".join([hit.payload["text"] for hit in hits]) if hits else ""
    prompt = f"""
    다음 공매 데이터를 참고하여 질문에 답하라.

    {context}

    질문: {q}
    """

    res = ollama.generate(model=GEN_MODEL, prompt=prompt)

    return {"answer": res["response"], "matches": len(hits)}
