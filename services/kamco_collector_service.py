"""
KAMCO 공매 데이터 수집 서비스

논리적 흐름:
1. 공매 공고 목록 조회 (getKamcoPlnmPbctList)
2. 각 공고에 대해:
   - 기본 정보 조회 (getKamcoPlnmPbctBasicInfoDetail)
   - 공매 일정 상세 조회 (getKamcoPlnmPbctBidDateInfoDetail)
   - 첨부 파일 정보 조회 (getKamcoPlnmPbctFileInfoDetail)
3. MongoDB에 저장
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import unquote

import requests
import xmltodict
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class KamcoCollectorService:
    """KAMCO 공매 데이터 수집 서비스"""
    
    def __init__(
        self,
        service_key: Optional[str] = None,
        mongo_uri: Optional[str] = None,
        db_name: str = "kamco",
        collection_name: str = "collected_items",
    ):
        # API 키 설정
        raw_key = service_key or os.getenv("KAMCO_SERVICE_KEY_ENCODED") or os.getenv("KAMCO_SERVICE_KEY_DECODED") or os.getenv("KAMCO_SERVICE_KEY")
        self.service_key = self._normalize_service_key(raw_key)
        
        if not self.service_key:
            raise ValueError("KAMCO service key is required")
        
        # API 설정
        self.base_url = "http://openapi.onbid.co.kr/openapi/services"
        self.service_path = "KamcoPblsalThingInquireSvc"
        self.timeout = 30
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
        # MongoDB 설정
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.collection = None
        
        # 통계
        self.stats = {
            "total_announces": 0,
            "processed_announces": 0,
            "failed_announces": 0,
            "saved_items": 0,
        }
    
    @staticmethod
    def _normalize_service_key(raw: Optional[str]) -> Optional[str]:
        """API 키 이중 인코딩 방지"""
        if not raw:
            return raw
        val = raw
        for _ in range(2):
            if "%" in val:
                val = unquote(val)
        return val
    
    def connect_mongodb(self) -> bool:
        """MongoDB 연결"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            db = self.client[self.db_name]
            self.collection = db[self.collection_name]
            return True
        except Exception as e:
            print(f"MongoDB 연결 실패: {e}")
            return False
    
    def close_mongodb(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
            self.client = None
            self.collection = None
    
    def fetch_announce_list(
        self,
        page_no: int = 1,
        num_of_rows: int = 10,
        prpt_dvsn_cd: str = "0001",
    ) -> Optional[List[Dict]]:
        """공매 공고 목록 조회"""
        url = f"{self.base_url}/{self.service_path}/getKamcoPlnmPbctList"
        params = {
            "serviceKey": self.service_key,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            "PRPT_DVSN_CD": prpt_dvsn_cd,
        }
        
        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            res.raise_for_status()
            
            payload = xmltodict.parse(res.text)
            header = (payload.get("response") or {}).get("header") or {}
            body = (payload.get("response") or {}).get("body") or {}
            
            result_code = str(header.get("resultCode"))
            if not result_code.startswith("0"):
                print(f"API 오류: resultCode={result_code}, resultMsg={header.get('resultMsg')}")
                return None
            
            items = body.get("items", {})
            item_list = items.get("item", [])
            
            if not item_list:
                return []
            
            return item_list if isinstance(item_list, list) else [item_list]
            
        except Exception as e:
            print(f"공고 목록 조회 실패: {e}")
            return None
    
    def fetch_basic_info(self, plnm_no: str, pbct_no: str) -> Optional[Dict]:
        """공매 공고 기본 정보 상세 조회"""
        url = f"{self.base_url}/{self.service_path}/getKamcoPlnmPbctBasicInfoDetail"
        params = {
            "serviceKey": self.service_key,
            "PLNM_NO": plnm_no,
            "PBCT_NO": pbct_no,
        }
        
        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            res.raise_for_status()
            
            payload = xmltodict.parse(res.text)
            header = (payload.get("response") or {}).get("header") or {}
            body = (payload.get("response") or {}).get("body") or {}
            
            result_code = str(header.get("resultCode"))
            if not result_code.startswith("0"):
                return None
            
            return body.get("item")
            
        except Exception as e:
            print(f"기본 정보 조회 실패 (PLNM_NO={plnm_no}, PBCT_NO={pbct_no}): {e}")
            return None
    
    def fetch_schedule_info(self, plnm_no: str, pbct_no: str) -> Optional[List[Dict]]:
        """공매 일정 상세 조회"""
        url = f"{self.base_url}/{self.service_path}/getKamcoPlnmPbctBidDateInfoDetail"
        params = {
            "serviceKey": self.service_key,
            "numOfRows": 10,
            "pageNo": 1,
            "PLNM_NO": plnm_no,
            "PBCT_NO": pbct_no,
        }
        
        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            res.raise_for_status()
            
            payload = xmltodict.parse(res.text)
            header = (payload.get("response") or {}).get("header") or {}
            body = (payload.get("response") or {}).get("body") or {}
            
            result_code = str(header.get("resultCode"))
            if not result_code.startswith("0"):
                return None
            
            items = body.get("items", {})
            bid_date_info = items.get("bidDateInfoItem", [])
            
            if not bid_date_info:
                return []
            
            return bid_date_info if isinstance(bid_date_info, list) else [bid_date_info]
            
        except Exception as e:
            print(f"일정 정보 조회 실패 (PLNM_NO={plnm_no}, PBCT_NO={pbct_no}): {e}")
            return None
    
    def fetch_file_info(self, plnm_no: str, pbct_no: str) -> Optional[List[Dict]]:
        """첨부 파일 정보 조회"""
        url = f"{self.base_url}/{self.service_path}/getKamcoPlnmPbctFileInfoDetail"
        params = {
            "serviceKey": self.service_key,
            "numOfRows": 10,
            "pageNo": 1,
            "PLNM_NO": plnm_no,
            "PBCT_NO": pbct_no,
        }
        
        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            res.raise_for_status()
            
            payload = xmltodict.parse(res.text)
            header = (payload.get("response") or {}).get("header") or {}
            body = (payload.get("response") or {}).get("body") or {}
            
            result_code = str(header.get("resultCode"))
            if not result_code.startswith("0"):
                return None
            
            items = body.get("items")
            if not items:
                return []
            
            file_info = items.get("fileItem", [])
            
            if not file_info:
                return []
            
            return file_info if isinstance(file_info, list) else [file_info]
            
        except Exception as e:
            print(f"첨부 파일 정보 조회 실패 (PLNM_NO={plnm_no}, PBCT_NO={pbct_no}): {e}")
            return None
    
    def collect_announce_details(self, announce: Dict) -> Optional[Dict]:
        """공고 상세 정보 수집 (기본정보 + 일정 + 첨부파일)"""
        plnm_no = announce.get("PLNM_NO")
        pbct_no = announce.get("PBCT_NO")
        
        if not plnm_no or not pbct_no:
            print(f"공고번호 또는 공매번호 누락: {announce}")
            return None
        
        # 기본 정보 조회
        basic_info = self.fetch_basic_info(plnm_no, pbct_no)
        time.sleep(0.2)  # API 호출 간격
        
        # 일정 정보 조회
        schedule_info = self.fetch_schedule_info(plnm_no, pbct_no)
        time.sleep(0.2)
        
        # 첨부 파일 정보 조회
        file_info = self.fetch_file_info(plnm_no, pbct_no)
        time.sleep(0.2)
        
        # 데이터 통합
        collected_data = {
            "PLNM_NO": plnm_no,
            "PBCT_NO": pbct_no,
            "announce_list_item": announce,
            "basic_info": basic_info,
            "schedule_info": schedule_info or [],
            "file_info": file_info or [],
            "collected_at": datetime.now(),
        }
        
        return collected_data
    
    def save_to_mongodb(self, data: Dict) -> bool:
        """MongoDB에 데이터 저장"""
        if self.collection is None:
            print("MongoDB 컬렉션이 초기화되지 않았습니다")
            return False
        
        try:
            # 중복 체크: PLNM_NO와 PBCT_NO로 확인
            existing = self.collection.find_one({
                "PLNM_NO": data["PLNM_NO"],
                "PBCT_NO": data["PBCT_NO"],
            })
            
            if existing:
                # 업데이트
                result = self.collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": data}
                )
                return result.modified_count > 0
            else:
                # 신규 삽입
                result = self.collection.insert_one(data)
                return result.inserted_id is not None
                
        except Exception as e:
            print(f"MongoDB 저장 실패: {e}")
            return False
    
    def run(
        self,
        page_no: int = 1,
        num_of_rows: int = 10,
        prpt_dvsn_cd: str = "0001",
        save_to_db: bool = True,
    ) -> Dict:
        """
        공매 데이터 수집 실행
        
        Args:
            page_no: 페이지 번호
            num_of_rows: 조회할 건수
            prpt_dvsn_cd: 재산구분코드 (0001: 금융권담보재산)
            save_to_db: MongoDB 저장 여부
            
        Returns:
            수집 결과 통계
        """
        print("=" * 80)
        print("KAMCO 공매 데이터 수집 시작")
        print("=" * 80)
        print(f"페이지: {page_no}, 조회건수: {num_of_rows}, 재산구분: {prpt_dvsn_cd}")
        print()
        
        # MongoDB 연결 (저장이 필요한 경우)
        if save_to_db:
            print("→ MongoDB 연결 중...")
            if not self.connect_mongodb():
                print("❌ MongoDB 연결 실패")
                return self.stats
            print(f"✅ MongoDB 연결 성공 ({self.db_name}.{self.collection_name})")
            print()
        
        # 1. 공고 목록 조회
        print("→ 공매 공고 목록 조회 중...")
        announces = self.fetch_announce_list(page_no, num_of_rows, prpt_dvsn_cd)
        
        if announces is None:
            print("❌ 공고 목록 조회 실패")
            self.close_mongodb()
            return self.stats
        
        if not announces:
            print("⚠️  조회된 공고가 없습니다")
            self.close_mongodb()
            return self.stats
        
        self.stats["total_announces"] = len(announces)
        print(f"✅ {len(announces)}개 공고 조회 완료")
        print()
        
        # 2. 각 공고의 상세 정보 수집
        print("→ 공고 상세 정보 수집 중...")
        for idx, announce in enumerate(announces, 1):
            plnm_no = announce.get("PLNM_NO", "N/A")
            pbct_no = announce.get("PBCT_NO", "N/A")
            print(f"  [{idx}/{len(announces)}] PLNM_NO: {plnm_no}, PBCT_NO: {pbct_no}")
            
            # 상세 정보 수집
            collected_data = self.collect_announce_details(announce)
            
            if not collected_data:
                print(f"    ❌ 수집 실패")
                self.stats["failed_announces"] += 1
                continue
            
            # MongoDB에 저장
            if save_to_db:
                if self.save_to_mongodb(collected_data):
                    print(f"    ✅ 저장 완료")
                    self.stats["saved_items"] += 1
                else:
                    print(f"    ⚠️  저장 실패")
            else:
                print(f"    ✅ 수집 완료 (저장 안함)")
            
            self.stats["processed_announces"] += 1
        
        print()
        print("=" * 80)
        print("수집 완료")
        print("=" * 80)
        print(f"전체 공고: {self.stats['total_announces']}개")
        print(f"처리 성공: {self.stats['processed_announces']}개")
        print(f"처리 실패: {self.stats['failed_announces']}개")
        if save_to_db:
            print(f"DB 저장: {self.stats['saved_items']}개")
        print("=" * 80)
        
        # MongoDB 연결 종료
        if save_to_db:
            self.close_mongodb()
        
        return self.stats
