"""
최신 공매 공고 조회 테스트

1. 최근 1년 공매 일정 조회
2. 해당 공고번호들의 상세 정보 조회
3. 첨부파일 조회

실행:
  python tests/test_latest_announces.py
"""

import os
import requests
import xmltodict
from dotenv import load_dotenv
from urllib.parse import unquote
from datetime import datetime, timedelta

load_dotenv()

# API 키 정규화
def _normalize_service_key(raw):
    if not raw:
        return raw
    val = raw
    for _ in range(2):
        if '%' in val:
            val = unquote(val)
    return val

SERVICE_KEY = _normalize_service_key(os.getenv('KAMCO_SERVICE_KEY_ENCODED'))
BASE_URL = "http://openapi.onbid.co.kr/openapi/services"
SERVICE_PATH = "KamcoPblsalThingInquireSvc"
TIMEOUT_SEC = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}


def get_latest_schedules(days=180, max_count=10):
    """최근 N일 내 공매 일정 조회"""
    url = f"{BASE_URL}/{SERVICE_PATH}/getKamcoPbctSchedule"
    
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 1,
        'numOfRows': max_count,
        'PRPT_DVSN_CD': '0001',
        'STRT_DT': start_date.strftime('%Y%m%d'),
        'END_DT': today.strftime('%Y%m%d')
    }
    
    print(f"\n{'='*100}")
    print(f"1. 최신 공매 일정 조회 (최근 {days}일)")
    print(f"{'='*100}")
    print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}")
    
    res = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SEC)
    payload = xmltodict.parse(res.text)
    body = payload.get('response', {}).get('body', {})
    items = body.get('items', {}).get('item', [])
    total = body.get('totalCount', 0)
    
    print(f"전체: {total}건")
    
    if not items:
        return []
    
    item_list = items if isinstance(items, list) else [items]
    
    # 공고번호별로 그룹핑 (중복 제거)
    announces = {}
    for item in item_list:
        plnm_no = item.get('PLNM_NO')
        pbct_no = item.get('PBCT_NO')
        if plnm_no and plnm_no not in announces:
            announces[plnm_no] = {
                'PLNM_NO': plnm_no,
                'PBCT_NO': pbct_no,
                'PBCT_BEGN_DTM': item.get('PBCT_BEGN_DTM'),
                'PBCT_CLS_DTM': item.get('PBCT_CLS_DTM'),
                'PBCT_EXCT_DTM': item.get('PBCT_EXCT_DTM')
            }
    
    announce_list = list(announces.values())[:max_count]
    
    print(f"\n조회된 공고 {len(announce_list)}건:")
    for i, item in enumerate(announce_list, 1):
        print(f"{i:2d}. 공고: {item['PLNM_NO']} | 공매: {item['PBCT_NO']}")
        print(f"     입찰: {item['PBCT_BEGN_DTM']} ~ {item['PBCT_CLS_DTM']}")
        print(f"     개찰: {item['PBCT_EXCT_DTM']}")
    
    return announce_list


def get_basic_info(plnm_no, pbct_no):
    """공고 기본 정보 조회"""
    url = f"{BASE_URL}/{SERVICE_PATH}/getKamcoPlnmPbctBasicInfoDetail"
    
    params = {
        'serviceKey': SERVICE_KEY,
        'PLNM_NO': plnm_no,
        'PBCT_NO': pbct_no
    }
    
    res = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SEC)
    payload = xmltodict.parse(res.text)
    body = (payload.get('response') or {}).get('body') or {}
    
    # API 응답 구조: body.item (items가 아님!)
    items = body.get('item')
    
    return items if items else None


def get_file_info(plnm_no, pbct_no):
    """첨부파일 정보 조회"""
    url = f"{BASE_URL}/{SERVICE_PATH}/getKamcoPlnmPbctFileInfoDetail"
    
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 1,
        'numOfRows': 100,
        'PLNM_NO': plnm_no,
        'PBCT_NO': pbct_no
    }
    
    res = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SEC)
    payload = xmltodict.parse(res.text)
    body = (payload.get('response') or {}).get('body') or {}
    items = (body.get('items') or {}).get('item') or []
    
    if not items:
        return []
    
    file_list = items if isinstance(items, list) else [items]
    
    # 파일번호로 중복 제거
    unique_files = {}
    for f in file_list:
        file_no = f.get('ATCH_FILE_PTCS_NO')
        if file_no and file_no not in unique_files:
            unique_files[file_no] = f
    
    return list(unique_files.values())


def main():
    if not SERVICE_KEY:
        print("❌ KAMCO_SERVICE_KEY_ENCODED is not set in .env")
        return 1
    
    # 1. 최신 일정 조회
    announces = get_latest_schedules(days=180, max_count=5)
    
    if not announces:
        print("\n⚠️  최근 6개월 내 공매 일정이 없습니다.")
        return 0
    
    # 2. 각 공고의 상세 정보 조회
    print(f"\n{'='*100}")
    print("2. 공고 상세 정보 조회")
    print(f"{'='*100}")
    
    for i, announce in enumerate(announces, 1):
        plnm_no = announce['PLNM_NO']
        pbct_no = announce['PBCT_NO']
        
        print(f"\n[{i}/{len(announces)}] 공고번호: {plnm_no}, 공매번호: {pbct_no}")
        print("-" * 100)
        
        # 기본 정보
        basic = get_basic_info(plnm_no, pbct_no)
        if basic:
            print(f"✅ 기본정보: {basic.get('PLNM_NM', 'N/A')[:60]}")
            print(f"   담당부서: {basic.get('RSBY_DEPT', 'N/A')}")
            print(f"   담당자: {basic.get('PSCG_NM', 'N/A')} ({basic.get('PSCG_TPNO', 'N/A')})")
        else:
            print("❌ 기본정보 없음")
        
        # 첨부파일
        files = get_file_info(plnm_no, pbct_no)
        if files:
            print(f"✅ 첨부파일: {len(files)}개")
            for j, f in enumerate(files, 1):
                print(f"   {j}. {f.get('ATCH_FILE_NM')} (파일번호: {f.get('ATCH_FILE_PTCS_NO')})")
        else:
            print("⚠️  첨부파일 없음")
    
    print(f"\n{'='*100}")
    print(f"✅ 테스트 완료: 최신 {len(announces)}개 공고 조회")
    print(f"{'='*100}")
    
    return 0


if __name__ == "__main__":
    exit(main())
