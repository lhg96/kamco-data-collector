"""
통합용도별물건목록조회 (getUnifyUsageCltr) 테스트

Usage:
  pytest tests/test_thing_usage_cltr.py -v
  RUN_INTEGRATION=1 pytest tests/test_thing_usage_cltr.py -v

Environment (.env):
  KAMCO_SERVICE_KEY_ENCODED
"""

import os
import pytest
import requests
import xmltodict
from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("KAMCO_SERVICE_KEY_ENCODED")
BASE_URL = "https://openapi.onbid.co.kr/openapi/services"
SERVICE_PATH = "ThingInfoInquireSvc"
OPERATION = "getUnifyUsageCltr"
TIMEOUT_SEC = 20

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr():
    """통합용도별물건목록조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/{OPERATION}"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 10,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    body = (payload.get("response") or {}).get("body") or {}

    result_code = str(header.get("resultCode"))
    result_msg = header.get("resultMsg")

    assert result_code.startswith("0"), f"API error: {result_code} - {result_msg}"

    items = (body.get("items") or {}).get("item")
    if items:
        print(f"✅ 통합용도별물건목록조회 성공: {len(items) if isinstance(items, list) else 1}개 조회")
    else:
        print("✅ 통합용도별물건목록조회 API 호출 성공 (데이터 없음)")


def test_parse_unify_usage_cltr_response():
    """통합용도별물건목록 응답 파싱 테스트"""
    mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>00</resultCode>
        <resultMsg>정상처리되었습니다</resultMsg>
    </header>
    <body>
        <items>
            <item>
                <cltrMnmtNo>202412-001-001</cltrMnmtNo>
                <pblancNo>2024-1234</pblancNo>
                <cltrNm>서울 강남구 아파트</cltrNm>
                <usgClcd>01</usgClcd>
                <usgClnm>아파트</usgClnm>
                <lctnAddr>서울특별시 강남구 역삼동</lctnAddr>
                <apprEvlAmt>500000000</apprEvlAmt>
                <mnmmSellPrc>400000000</mnmmSellPrc>
            </item>
        </items>
        <numOfRows>1</numOfRows>
        <pageNo>1</pageNo>
        <totalCount>150</totalCount>
    </body>
</response>"""

    payload = xmltodict.parse(mock_xml)
    header = payload["response"]["header"]
    body = payload["response"]["body"]

    assert header["resultCode"] == "00"
    assert header["resultMsg"] == "정상처리되었습니다"

    items = body["items"]["item"]
    assert items["cltrMnmtNo"] == "202412-001-001"
    assert items["cltrNm"] == "서울 강남구 아파트"
    assert items["usgClnm"] == "아파트"
    assert items["lctnAddr"] == "서울특별시 강남구 역삼동"
    assert body["totalCount"] == "150"

    print("✅ 통합용도별물건목록 응답 파싱 성공")
