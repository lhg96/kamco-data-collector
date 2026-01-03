"""Embed normalized KAMCO documents and upsert them into Qdrant."""

import hashlib
import logging
import os
import uuid

import ollama
from dotenv import load_dotenv
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "kamco")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")

qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
mongo = MongoClient(MONGO_URI)
docs = mongo.kamco.normalized_items


def setup_collection() -> None:
    """Create or recreate Qdrant collection"""
    try:
        qdrant.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )
        logger.info(f"Collection '{COLLECTION}' created/recreated with 768 dimensions for nomic-embed-text")
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise


def embed() -> int:
    """
    Embed normalized documents and store in Qdrant
    Returns: number of embedded documents
    """
    count = 0
    errors = 0
    
    logger.info(f"Starting embedding process with model: {EMBED_MODEL}")
    
    for doc in docs.find():
        try:
            # Generate embedding
            text = doc.get("text", "")
            if not text:
                logger.warning(f"Skipping document {doc['_id']}: empty text")
                continue
                
            emb = ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]
            
            # Prepare payload
            payload = {
                "text": text,
                "source": doc.get("source", "unknown"),
                "normalized_at": doc.get("normalized_at"),
            }
            
            # Add metadata if available
            if "metadata" in doc:
                payload["metadata"] = doc["metadata"]
            
            # Convert MongoDB ObjectId to UUID
            # Use MD5 hash of ObjectId string to generate UUID
            doc_id_str = str(doc["_id"])
            doc_uuid = str(uuid.UUID(hashlib.md5(doc_id_str.encode()).hexdigest()))
            
            # Store original MongoDB ID in payload for reference
            payload["mongodb_id"] = doc_id_str
            
            # Upsert to Qdrant
            qdrant.upsert(
                collection_name=COLLECTION,
                points=[
                    {
                        "id": doc_uuid,
                        "vector": emb,
                        "payload": payload,
                    }
                ],
            )
            count += 1
            
            if count % 10 == 0:
                logger.info(f"Embedded {count} documents...")
                
        except Exception as e:
            logger.error(f"Error embedding document {doc.get('_id')}: {e}")
            errors += 1
            continue
    
    logger.info(f"Embedding completed: {count} documents embedded, {errors} errors")
    return count


if __name__ == "__main__":
    setup_collection()
    embed()
