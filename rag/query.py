"""Shared RAG query logic for KAMCO collector."""

import logging
import os
from typing import List, Dict, Optional, Union
from datetime import datetime

import ollama
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from pymongo import MongoClient, DESCENDING
import string

load_dotenv()

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "kamco")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:12b")
TOP_K = int(os.getenv("TOP_K", "5"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
start_clients = True
qdrant = None
db = None

if start_clients:
    try:
        qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {e}")

    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        db = mongo_client.kamco
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB client: {e}")


def get_latest_documents(limit: int = 5) -> List[Dict]:
    """Fetch latest documents directly from MongoDB"""
    if db is None:
        logger.warning("MongoDB not connected, cannot fetch latest documents.")
        return []
    
    docs = []
    try:
        cursor = db.normalized_items.find().sort("normalized_at", DESCENDING).limit(limit)
        for doc in cursor:
            docs.append({
                "id": str(doc["_id"]),
                "score": 1.0, # Artificial high score for latest items
                "text": doc.get("text", "")
            })
            
        if not docs:
             cursor = db.collected_items.find().sort("collected_at", DESCENDING).limit(limit)
             from normalize.kamco_normalizer import _build_text_from_collected
             for doc in cursor:
                 text = _build_text_from_collected(doc)
                 docs.append({
                     "id": str(doc["_id"]),
                     "score": 1.0,
                     "text": text
                 })
                 
    except Exception as e:
        logger.error(f"Error fetching latest documents: {e}")
    
    return docs


def search_vector(query: str, limit: int = TOP_K) -> List[Dict]:
    """Search Qdrant for similar documents"""
    if not qdrant:
        logger.error("Qdrant client not ready")
        return []
        
    try:
        # Generate embedding for query
        emb = ollama.embeddings(model=EMBED_MODEL, prompt=query)["embedding"]
        
        # Search Qdrant
        results = qdrant.search(
            collection_name=COLLECTION,
            query_vector=emb,
            limit=limit,
            with_payload=True
        )
        
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "text": result.payload.get("text", "")
            }
            for result in results
        ]
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []

def keyword_search(query: str, limit: int = 5) -> List[Dict]:
    """Search using MongoDB text/regex match (Exact/Partial Match)"""
    if db is None:
        return []
        
    # Pre-process query to remove punctuation
    cleaned_query = query.translate(str.maketrans('', '', string.punctuation))
    
    # extract keywords (naively split by space, ignore common words)
    ignore = ["공고명", "공고", "찾아줘", "검색", "보여줘", "알려줘", "대한", "정보", "찾아", "공매", "있는", "하는", "건은", "경우"]
    keywords = [w for w in cleaned_query.split() if w not in ignore and len(w) > 1]
    
    if not keywords:
        return []
        
    regex_pattern = "|".join([f"({k})" for k in keywords])
    
    docs = []
    try:
        # Increase internal limit to gather candidates, then rank
        cursor = db.normalized_items.find({
            "text": {"$regex": regex_pattern, "$options": "i"}
        }).limit(50) 
        
        candidates = []
        for doc in cursor:
            text = doc.get("text", "")
            match_count = sum(1 for k in keywords if k in text)
            if match_count > 0:
                candidates.append({
                    "id": str(doc["_id"]),
                    "text": text,
                    "match_count": match_count
                })
        
        candidates.sort(key=lambda x: x["match_count"], reverse=True)
        
        for c in candidates[:limit]:
            docs.append({
                "id": c["id"],
                "score": 0.99, 
                "text": c["text"]
            })
                
    except Exception as e:
        logger.error(f"Keyword search error: {e}")
        
    return docs


def smart_search(query: str, limit: int = TOP_K) -> List[Dict]:
    """
    Intelligent search: Latest -> Keyword -> Vector
    """
    query_lower = query.lower()
    
    # 1. Latest Data
    time_keywords = ["최신", "최근", "latest", "recent", "마지막", "new", "수집 자료"]
    is_specific_year = any(y in query for y in ["2023", "2024", "2025", "2026"])
    
    if any(k in query_lower for k in time_keywords) and not is_specific_year: 
        logger.info(f"Detected time-based query: '{query}'")
        return get_latest_documents(limit)
    
    # 2. Keyword Search (for specific titles or short queries)
    keyword_results = []
    # Trigger if specific keywords present OR query is short enough to be a specific lookup
    triggers = ["공고", "공매", "찾아", "검색", "번호", "20", "제", "위치", "가격", "언제", "어디"]
    
    should_keyword_search = any(t in query for t in triggers) or len(query) < 50
    
    if should_keyword_search:
        logger.info(f"Detected potential Title/Keyword query: '{query}'")
        keyword_results = keyword_search(query, limit)
    
    # 3. Vector Search (Semantic)
    vector_results = search_vector(query, limit)
    
    # 4. Combine (Deduplicate by ID)
    seen_ids = set()
    final_results = []
    
    # Prioritize Keyword results
    for r in keyword_results:
        if r['id'] not in seen_ids:
            final_results.append(r)
            seen_ids.add(r['id'])
            
    # Add Vector results filling the rest
    for r in vector_results:
        if r['id'] not in seen_ids:
            final_results.append(r)
            seen_ids.add(r['id'])
            
    return final_results[:limit]


def generate_answer(question: str, context_docs: List[Dict]) -> str:
    """Generate answer using LLM with context"""
    try:
        # Build context
        context = "\n\n".join([
            f"[문서 {i+1}] (관련도: {doc['score']:.2f})\n{doc['text']}"
            for i, doc in enumerate(context_docs)
        ])
        
        if not context:
            return "관련된 정보를 찾을 수 없습니다."

        prompt = f"""You are a helpful assistant for KAMCO (Korea Asset Management Corporation) auctions.
Based on the following context, answer the user's question.

Context:
{context}

Question: {question}

Instructions:
1. Answer in Korean.
2. Cite the source document number if possible.
3. If asking for "latest" or "recent" data, list the items from the context clearly.
4. If the answer is not in the context, say "제공된 문서에서 정보를 찾을 수 없습니다."
5. Be concise and helpful.
"""
        response = ollama.generate(model=LLM_MODEL, prompt=prompt)
        return response["response"]
    except Exception as e:
        logger.error(f"Generate answer error: {e}")
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"
