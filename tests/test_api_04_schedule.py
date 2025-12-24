"""
4. 캠코공매일정조회 (getKamcoPbctSchedule)

실행:
  python tests/test_api_04_schedule.py

환경변수 (.env):
  KAMCO_SERVICE_KEY_ENCODED

샘플 URL:
http://openapi.onbid.co.kr/openapi/services/KamcoPblsalThingInquireSvc/getKamcoPbctSchedule
"""

import os
import sys
import requests
import xmltodict
from dotenv import load_dotenv
from urllib.parse import unquote
from datetime import datetime, timedelta

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
OPERATION = "getKamcoPbctSchedule"
TIMEOUT_SEC = 30

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def main() -> int:
    # 날짜 범위 설정 (최근 30일)
    today = datetime.now()
    date_from = (today - timedelta(days=30)).strftime("%Y%m%d")
    date_to = today.strftime("%Y%m%d")

    url = f"{BASE_URL}/{SERVICE_PATH}/{OPERATION}"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 10,
        "PRPT_DVSN_CD": "0001",  # 재산구분코드
        "PBCT_BEGN_FROM": date_from,  # 입찰시작일자(FROM)
        "PBCT_CLS_TO": date_to,  # 입찰종료일자(TO)
    }

    print(f"→ GET {url}")
    print(f"   params: pageNo=1, numOfRows=10, PRPT_DVSN_CD=0001")
    print(f"   날짜범위: {date_from} ~ {date_to}")
    
    try:
        res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
        res.raise_for_status()
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Connection timeout. 네트워크 상태를 확인하거나 VPN 연결을 시도하세요.")
        return 2
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

    if not result_code.startswith("0"):
        print(f"❌ API error")
        return 3

    items = (body.get("items") or {}).get("item")
    total_count = body.get("totalCount", "0")
    
    if items:
        item_list = items if isinstance(items, list) else [items]
        print(f"✅ 캠코공매일정조회 성공: {len(item_list)}개 조회 (전체: {total_count})")
        
        print("\n첫 번째 일정 정보:")
        first = item_list[0]
        for k, v in list(first.items())[:8]:
            print(f"   {k}: {v}")
    else:
        print("✅ API 호출 성공 (데이터 없음)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
