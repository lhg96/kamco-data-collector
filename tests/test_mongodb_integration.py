"""
MongoDB 연결 및 KAMCO API 데이터 저장 통합 테스트

실행:
  python tests/test_mongodb_integration.py

환경변수 (.env):
  KAMCO_SERVICE_KEY_ENCODED - KAMCO API 키
  MONGO_URI - MongoDB 연결 URI (기본값: mongodb://localhost:27017)
  MONGO_DB_NAME - MongoDB 데이터베이스 이름 (기본값: kamco)
  MONGO_COLLECTION_NAME - MongoDB 컬렉션 이름 (기본값: test_items)
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import requests
import xmltodict
from urllib.parse import unquote

load_dotenv()

# API 키 정규화
RAW_SERVICE_KEY = (
    os.getenv("KAMCO_SERVICE_KEY_ENCODED")
    or os.getenv("KAMCO_SERVICE_KEY_DECODED")
    or os.getenv("KAMCO_SERVICE_KEY")
)

def _normalize_service_key(raw: str | None) -> str | None:
    """이중 인코딩 방지를 위해 디코딩"""
    if not raw:
        return raw
    val = raw
    for _ in range(2):
        if "%" in val:
            val = unquote(val)
    return val

SERVICE_KEY = _normalize_service_key(RAW_SERVICE_KEY)

# MongoDB 설정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "kamco")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "test_items")

# KAMCO API 설정
BASE_URL = "http://openapi.onbid.co.kr/openapi/services"
SERVICE_PATH = "KamcoPblsalThingInquireSvc"
TIMEOUT_SEC = 30

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def test_mongodb_connection():
    """MongoDB 연결 테스트"""
    print("=" * 80)
    print("1. MongoDB 연결 테스트")
    print("=" * 80)
    print(f"→ MongoDB URI: {MONGO_URI}")
    print(f"→ Database: {MONGO_DB_NAME}")
    print(f"→ Collection: {MONGO_COLLECTION_NAME}")
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # 연결 확인
        client.admin.command('ping')
        
        print("✅ MongoDB 연결 성공")
        
        # 서버 정보 출력
        server_info = client.server_info()
        print(f"   MongoDB 버전: {server_info.get('version', 'unknown')}")
        
        # 데이터베이스 목록
        db_list = client.list_database_names()
        print(f"   사용 가능한 데이터베이스: {', '.join(db_list[:5])}")
        
        return client
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return None


def test_fetch_kamco_api():
    """KAMCO API 데이터 조회 테스트"""
    print("\n" + "=" * 80)
    print("2. KAMCO API 데이터 조회 테스트")
    print("=" * 80)
    
    if not SERVICE_KEY:
        print("❌ KAMCO_SERVICE_KEY_ENCODED is not set in .env")
        return None
    
    url = f"{BASE_URL}/{SERVICE_PATH}/getKamcoPbctCltrList"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 5,  # 테스트용으로 5개만 조회
        "DPSL_MTD_CD": "0001",
    }
    
    print(f"→ GET {url}")
    print(f"   params: pageNo=1, numOfRows=5, DPSL_MTD_CD=0001")
    
    try:
        res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
        res.raise_for_status()
        
        payload = xmltodict.parse(res.text)
        header = (payload.get("response") or {}).get("header") or {}
        body = (payload.get("response") or {}).get("body") or {}
        
        result_code = str(header.get("resultCode"))
        result_msg = header.get("resultMsg")
        
        print(f"   resultCode: {result_code}")
        print(f"   resultMsg: {result_msg}")
        
        if not result_code.startswith("0"):
            print(f"❌ API 오류")
            return None
        
        total_count = body.get("totalCount", 0)
        items = body.get("items", {})
        item_list = items.get("item", [])
        
        if not item_list:
            print("❌ 조회된 데이터 없음")
            return None
        
        count = len(item_list) if isinstance(item_list, list) else 1
        print(f"✅ KAMCO API 데이터 조회 성공: {count}개 (전체: {total_count})")
        
        # 첫 번째 아이템 정보 출력
        first_item = item_list[0] if isinstance(item_list, list) else item_list
        print(f"\n첫 번째 물건 정보:")
        for k, v in list(first_item.items())[:5]:
            print(f"   {k}: {v}")
        
        return item_list if isinstance(item_list, list) else [item_list]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {e}")
        return None
    except Exception as e:
        print(f"❌ 데이터 파싱 실패: {e}")
        return None


def test_save_to_mongodb(client, items):
    """MongoDB에 데이터 저장 테스트"""
    print("\n" + "=" * 80)
    print("3. MongoDB에 데이터 저장 테스트")
    print("=" * 80)
    
    if not client:
        print("❌ MongoDB 클라이언트가 없습니다")
        return False
    
    if not items:
        print("❌ 저장할 데이터가 없습니다")
        return False
    
    try:
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        
        print(f"→ 데이터베이스: {MONGO_DB_NAME}")
        print(f"→ 컬렉션: {MONGO_COLLECTION_NAME}")
        print(f"→ 저장할 아이템 수: {len(items)}")
        
        # 타임스탬프 추가
        for item in items:
            item["_saved_at"] = datetime.now()
            item["_test_data"] = True
        
        # 데이터 삽입
        result = collection.insert_many(items)
        inserted_count = len(result.inserted_ids)
        
        print(f"✅ MongoDB에 데이터 저장 성공: {inserted_count}개 저장됨")
        print(f"   삽입된 ID: {result.inserted_ids[:3]}..." if len(result.inserted_ids) > 3 else f"   삽입된 ID: {result.inserted_ids}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 저장 실패: {e}")
        return False


def test_verify_saved_data(client):
    """저장된 데이터 검증 테스트"""
    print("\n" + "=" * 80)
    print("4. 저장된 데이터 검증 테스트")
    print("=" * 80)
    
    if not client:
        print("❌ MongoDB 클라이언트가 없습니다")
        return False
    
    try:
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        
        # 테스트 데이터 카운트
        test_data_count = collection.count_documents({"_test_data": True})
        print(f"→ 테스트 데이터 카운트: {test_data_count}개")
        
        if test_data_count == 0:
            print("❌ 저장된 테스트 데이터가 없습니다")
            return False
        
        # 최근 저장된 데이터 조회
        recent_items = list(collection.find({"_test_data": True}).sort("_saved_at", -1).limit(3))
        
        print(f"✅ 저장된 데이터 검증 성공")
        print(f"\n최근 저장된 데이터 (최대 3개):")
        for idx, item in enumerate(recent_items, 1):
            print(f"\n   [{idx}] ID: {item.get('_id')}")
            print(f"       PLNM_NO: {item.get('PLNM_NO', 'N/A')}")
            print(f"       PBCT_NO: {item.get('PBCT_NO', 'N/A')}")
            print(f"       저장 시간: {item.get('_saved_at', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 검증 실패: {e}")
        return False


def cleanup_test_data(client):
    """테스트 데이터 정리"""
    print("\n" + "=" * 80)
    print("5. 테스트 데이터 정리")
    print("=" * 80)
    
    if not client:
        print("⚠️  MongoDB 클라이언트가 없어 정리를 건너뜁니다")
        return
    
    try:
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        
        # 테스트 데이터 삭제
        result = collection.delete_many({"_test_data": True})
        deleted_count = result.deleted_count
        
        print(f"✅ 테스트 데이터 정리 완료: {deleted_count}개 삭제됨")
        
    except Exception as e:
        print(f"❌ 테스트 데이터 정리 실패: {e}")


def main() -> int:
    print("=" * 80)
    print("MongoDB 연결 및 KAMCO API 데이터 저장 통합 테스트")
    print("=" * 80)
    print()
    
    # 1. MongoDB 연결 테스트
    client = test_mongodb_connection()
    if not client:
        print("\n" + "=" * 80)
        print("❌ MongoDB 연결 실패로 테스트를 중단합니다")
        print("=" * 80)
        return 1
    
    # 2. KAMCO API 데이터 조회
    items = test_fetch_kamco_api()
    if not items:
        print("\n" + "=" * 80)
        print("❌ KAMCO API 데이터 조회 실패로 테스트를 중단합니다")
        print("=" * 80)
        client.close()
        return 2
    
    # 3. MongoDB에 데이터 저장
    save_success = test_save_to_mongodb(client, items)
    if not save_success:
        print("\n" + "=" * 80)
        print("❌ 데이터 저장 실패")
        print("=" * 80)
        client.close()
        return 3
    
    # 4. 저장된 데이터 검증
    verify_success = test_verify_saved_data(client)
    if not verify_success:
        print("\n" + "=" * 80)
        print("❌ 데이터 검증 실패")
        print("=" * 80)
        cleanup_test_data(client)
        client.close()
        return 4
    
    # 5. 테스트 데이터 정리
    cleanup_test_data(client)
    
    # MongoDB 연결 종료
    client.close()
    
    print("\n" + "=" * 80)
    print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
