"""
5. 캠코공매공고 공매일정 상세조회 (getKamcoPlnmPbctBidDateInfoDetail)

실행:
  python tests/test_api_05_announce_schedule.py

환경변수 (.env):
  KAMCO_SERVICE_KEY_ENCODED
  TEST_PLNM_NO (선택, 기본값: 공고목록에서 자동 조회)
  TEST_PBCT_NO (선택, 기본값: 공고목록에서 자동 조회)

샘플 URL:
http://openapi.onbid.co.kr/openapi/services/KamcoPblsalThingInquireSvc/getKamcoPlnmPbctBidDateInfoDetail
파라미터: PLNM_NO, PBCT_NO
"""

import os
import sys
import requests
import xmltodict
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

# API 키 정규화: 이중 인코딩 방지
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
BASE_URL = "http://openapi.onbid.co.kr/openapi/services"
SERVICE_PATH = "KamcoPblsalThingInquireSvc"
TIMEOUT_SEC = 30

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def get_first_plnm_pbct_no() -> tuple[str, str]:
    """공고목록에서 첫 번째 공고번호(PLNM_NO)와 공매번호(PBCT_NO)를 가져옵니다."""
    url = f"{BASE_URL}/{SERVICE_PATH}/getKamcoPlnmPbctList"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 1,
        "PRPT_DVSN_CD": "0001",
    }
    
    try:
        res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
        res.raise_for_status()
        payload = xmltodict.parse(res.text)
        body = (payload.get("response") or {}).get("body") or {}
        items = (body.get("items") or {}).get("item")
        
        if items:
            first_item = items[0] if isinstance(items, list) else items
            return first_item.get("PLNM_NO", ""), first_item.get("PBCT_NO", "")
    except:
        pass
    
    return "", ""


def main() -> int:
    if not SERVICE_KEY:
        print("❌ KAMCO_SERVICE_KEY_ENCODED is not set in .env")
        return 1

    # 공고번호와 공매번호 가져오기
    plnm_no = os.getenv("TEST_PLNM_NO", "")
    pbct_no = os.getenv("TEST_PBCT_NO", "")
    
    if not plnm_no or not pbct_no:
        print("→ TEST_PLNM_NO 또는 TEST_PBCT_NO가 설정되지 않음. 공고목록에서 자동 조회...")
        plnm_no, pbct_no = get_first_plnm_pbct_no()
        
        if not plnm_no or not pbct_no:
            print("❌ 공고번호 또는 공매번호를 가져올 수 없습니다.")
            return 1

    print(f"→ 사용할 공고번호(PLNM_NO): {plnm_no}")
    print(f"→ 사용할 공매번호(PBCT_NO): {pbct_no}")

    url = f"{BASE_URL}/{SERVICE_PATH}/getKamcoPlnmPbctBidDateInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "PLNM_NO": plnm_no,
        "PBCT_NO": pbct_no,
    }

    print(f"→ GET {url}")
    print(f"   params: numOfRows=10, pageNo=1, PLNM_NO={plnm_no}, PBCT_NO={pbct_no}")
    
    try:
        res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
        res.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"❌ Request failed: {exc}")
        return 2

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    body = (payload.get("response") or {}).get("body") or {}
    
    result_code = str(header.get("resultCode"))
    result_msg = header.get("resultMsg")

    print(f"   resultCode: {result_code}")
    print(f"   resultMsg: {result_msg}")

    if result_code == "03":
        print("✅ API 호출 성공 (해당 공고에 대한 일정 데이터 없음)")
        return 0

    if not result_code.startswith("0"):
        print(f"❌ API error")
        return 3

    total_count = body.get("totalCount", 0)
    items = body.get("items", {})
    bid_date_info_list = items.get("bidDateInfoItem", [])
    
    if bid_date_info_list:
        count = len(bid_date_info_list) if isinstance(bid_date_info_list, list) else 1
        print(f"✅ 캠코공매공고 공매일정 상세조회 성공: {count}개 조회 (전체: {total_count})")
        
        first_item = bid_date_info_list[0] if isinstance(bid_date_info_list, list) else bid_date_info_list
        print("\n공매일정 상세정보 (첫 번째):")
        for k, v in first_item.items():
            print(f"   {k}: {v}")
    else:
        print("✅ API 호출 성공 (데이터 없음)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
