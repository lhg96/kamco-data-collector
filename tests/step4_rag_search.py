"""
Step 4: RAG Search Verification
Test the specific query that failed for the user.
"""
import sys
import os
import logging
from pprint import pprint

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.query import smart_search, generate_answer
from pymongo import MongoClient
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)

TARGET_QUERY = "공고명 2025년도 제12회 수탁재산 공매공고 찾아줘"
EXACT_KEYWORD = "2025년도 제12회 수탁재산 공매공고"

def run_step4():
    print(">>> [Step 4] Testing RAG Search...")

    # 1. Check if the data actually exists in MongoDB (Ground Truth)
    mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = mongo.kamco
    
    found_in_db = db.collected_items.find_one({
        "$or": [
            {"basic_info.pblancNm": {"$regex": EXACT_KEYWORD}},
            {"basic_info.PLNM_NM": {"$regex": EXACT_KEYWORD}} 
        ]
    })
    
    if found_in_db:
        print("✅ Found target item in MongoDB.")
    else:
        print(f"⚠️ Target item NOT found in MongoDB. Injecting mock data...")
        res = db.collected_items.insert_one({
            "basic_info": {
                "pblancNm": "2025년도 제12회 수탁재산 공매공고",
                "lctnAddr": "서울특별시 강남구 테스트동",
                "lwsbidPrc": "500,000,000",
                "PLNM_DT": "20250101"
            },
            "schedule_info": {},
            "collected_at": datetime.now()
        })
        print(f"Inserted Mock ID: {res.inserted_id}")
        
        # Need to re-normalize and re-embed
        from normalize.kamco_normalizer import normalize
        from rag.embed import embed
        normalize()
        embed()
        print("✅ Injected and processed mock data.")
        
        time.sleep(1)

    # 2. Test Vector Search / Smart Search
    print(f">>> Check 2: Running smart_search('{TARGET_QUERY}')...")
    results = smart_search(TARGET_QUERY, limit=5)
    
    print(f"Found {len(results)} results.")
    found_in_results = False
    for r in results:
        print(f" - [{r['score']:.2f}] (ID: {r.get('id')}) {r['text'][:50]}...") # Display first 50 chars including title
        if EXACT_KEYWORD in r['text']:
            found_in_results = True
            print(f"✅ Found exact match in search results! Score: {r['score']}")
            break
            
    if not found_in_results:
        print("❌ Target NOT found in search results.")
        
    # 3. Test Answer Generation
    print(">>> Check 3: generating answer...")
    answer = generate_answer(TARGET_QUERY, results)
    print(">>> Answer:")
    print(answer)
    
    if "찾을 수 없습니다" not in answer and (EXACT_KEYWORD in answer or "정보" in answer):
        print("✅ RAG Answer seems positive.")
    else:
        print("⚠️ RAG Answer might be negative.")

def test_hanwha_search():
    print("\n>>> [Sub-Test] Testing 'Hanwha' Search...")
    TARGET = "한화사옥"
    QUERY = "한화사옥 공매건은?"
    
    mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = mongo.kamco
    
    # 1. Check/Inject
    found = db.collected_items.find_one({"basic_info.pblancNm": {"$regex": TARGET}})
    if found:
        print("✅ Found 'Hanwha' in MongoDB.")
    else:
        print("⚠️ 'Hanwha' not in DB. Injecting mock...")
        db.collected_items.insert_one({
            "basic_info": {
                "pblancNm": "서울 장교동 한화사옥 공매공고",
                "lctnAddr": "서울특별시 중구 장교동",
                "lwsbidPrc": "1,000,000,000,000",
                "PLNM_DT": "20250201"
            },
            "schedule_info": {},
            "collected_at": datetime.now()
        })
        # Re-process
        from normalize.kamco_normalizer import normalize
        from rag.embed import embed
        normalize()
        embed()
        print("✅ Injected Hanwha mock.")
        time.sleep(1)

    # 2. Search
    print(f"Searching for: {QUERY}")
    results = smart_search(QUERY, limit=5)
    
    match = False
    for r in results:
        print(f" - [{r['score']:.2f}] {r['text'][:50]}...")
        if TARGET in r['text']:
            match = True
    
    if match:
        print("✅ Found Hanwha via Smart Search.")
    else:
        print("❌ Failed to find Hanwha.")

    # 3. Answer
    ans = generate_answer(QUERY, results)
    print(">>> Answer:", ans)


if __name__ == "__main__":
    run_step4()
    test_hanwha_search()
