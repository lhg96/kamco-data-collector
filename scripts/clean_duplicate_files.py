"""MongoDB에 저장된 중복 첨부파일 정리"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "kamco")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "collected_items")

print("=" * 80)
print("MongoDB 첨부파일 중복 제거")
print("=" * 80)

try:
    # MongoDB 연결
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    
    print(f"✅ MongoDB 연결 성공 ({MONGO_DB_NAME}.{MONGO_COLLECTION_NAME})")
    
    # 첨부파일이 있는 모든 문서 조회
    total = collection.count_documents({"file_info": {"$exists": True, "$ne": []}})
    print(f"→ 첨부파일이 있는 문서: {total}개")
    print()
    
    updated_count = 0
    removed_dup_count = 0
    
    for doc in collection.find({"file_info": {"$exists": True, "$ne": []}}):
        file_info = doc.get("file_info", [])
        
        if not file_info:
            continue
        
        # 중복 제거
        seen = set()
        unique_files = []
        for file in file_info:
            file_id = file.get('ATCH_FILE_PTCS_NO')
            if file_id and file_id not in seen:
                seen.add(file_id)
                unique_files.append(file)
        
        # 중복이 있었다면 업데이트
        if len(unique_files) < len(file_info):
            dup_count = len(file_info) - len(unique_files)
            print(f"  PLNM_NO: {doc.get('PLNM_NO')}, PBCT_NO: {doc.get('PBCT_NO')}")
            print(f"    중복 {dup_count}개 제거 ({len(file_info)}개 → {len(unique_files)}개)")
            
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"file_info": unique_files}}
            )
            
            updated_count += 1
            removed_dup_count += dup_count
    
    print()
    print("=" * 80)
    print("정리 완료")
    print("=" * 80)
    print(f"업데이트된 문서: {updated_count}개")
    print(f"제거된 중복 파일: {removed_dup_count}개")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
