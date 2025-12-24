"""
통합용도별물건 상세정보 조회 테스트
- 기본정보 (getUnifyUsageCltrBasicInfoDetail)
- 감정평가서정보 (getUnifyUsageCltrEstimationInfoDetail)
- 임대차정보 (getUnifyUsageCltrRentalInfoDetail)
- 권리종류정보 (getUnifyUsageCltrRegisteredInfoDetail)
- 공매일정 (getUnifyUsageCltrBidDateInfoDetail)
- 입찰이력 (getUnifyUsageCltrBidHistoryInfoDetail)
- 주주정보 (getUnifyUsageCltrStockholderInfoDetail)
- 법인현황정보 (getUnifyUsageCltrCorporatebodyInfoDetail)

Usage:
  pytest tests/test_thing_usage_details.py -v
  RUN_INTEGRATION=1 pytest tests/test_thing_usage_details.py -v

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
TIMEOUT_SEC = 20

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 실제 테스트용 물건관리번호 (테스트시 유효한 값으로 변경)
TEST_CLTR_MNMT_NO = os.getenv("TEST_CLTR_MNMT_NO", "202412-001-001")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_basic_info_detail():
    """통합용도별물건 기본정보 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrBasicInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))
    result_msg = header.get("resultMsg")

    assert result_code in ["00", "03"], f"API error: {result_code} - {result_msg}"
    print(f"✅ 통합용도별물건 기본정보 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_estimation_info_detail():
    """통합용도별물건 감정평가서정보 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrEstimationInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 감정평가서정보 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_rental_info_detail():
    """통합용도별물건 임대차정보 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrRentalInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 임대차정보 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_registered_info_detail():
    """통합용도별물건 권리종류정보 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrRegisteredInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 권리종류정보 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_bid_date_info_detail():
    """통합용도별물건 공매일정 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrBidDateInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 공매일정 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_bid_history_info_detail():
    """통합용도별물건 입찰이력 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrBidHistoryInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 입찰이력 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_stockholder_info_detail():
    """통합용도별물건 주주정보 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrStockholderInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 주주정보 상세조회 성공: resultCode={result_code}")


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_get_unify_usage_cltr_corporatebody_info_detail():
    """통합용도별물건 법인현황정보 상세조회 API 호출 테스트"""
    if not SERVICE_KEY:
        pytest.skip("KAMCO_SERVICE_KEY_ENCODED is not set")

    url = f"{BASE_URL}/{SERVICE_PATH}/getUnifyUsageCltrCorporatebodyInfoDetail"
    params = {
        "serviceKey": SERVICE_KEY,
        "cltrMnmtNo": TEST_CLTR_MNMT_NO,
    }

    res = requests.get(url, params=params, headers=BROWSER_HEADERS, timeout=TIMEOUT_SEC)
    res.raise_for_status()

    payload = xmltodict.parse(res.text)
    header = (payload.get("response") or {}).get("header") or {}
    result_code = str(header.get("resultCode"))

    assert result_code in ["00", "03"]
    print(f"✅ 통합용도별물건 법인현황정보 상세조회 성공: resultCode={result_code}")


def test_parse_basic_info_response():
    """통합용도별물건 기본정보 응답 파싱 테스트"""
    mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>00</resultCode>
        <resultMsg>정상처리되었습니다</resultMsg>
    </header>
    <body>
        <item>
            <cltrMnmtNo>202412-001-001</cltrMnmtNo>
            <pblancNo>2024-1234</pblancNo>
            <cltrNm>서울 강남구 아파트</cltrNm>
            <usgClcd>01</usgClcd>
            <usgClnm>아파트</usgClnm>
            <lctnAddr>서울특별시 강남구 역삼동 123-45</lctnAddr>
            <lndclsNm>대지</lndclsNm>
            <lndArea>100.5</lndArea>
            <bdlArea>85.3</bdlArea>
            <apprEvlAmt>500000000</apprEvlAmt>
            <mnmmSellPrc>400000000</mnmmSellPrc>
        </item>
    </body>
</response>"""

    payload = xmltodict.parse(mock_xml)
    header = payload["response"]["header"]
    body = payload["response"]["body"]

    assert header["resultCode"] == "00"
    item = body["item"]
    assert item["cltrMnmtNo"] == "202412-001-001"
    assert item["cltrNm"] == "서울 강남구 아파트"
    assert item["usgClnm"] == "아파트"
    assert item["lndArea"] == "100.5"

    print("✅ 통합용도별물건 기본정보 응답 파싱 성공")
