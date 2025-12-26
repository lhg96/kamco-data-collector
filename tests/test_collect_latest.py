"""
최신 공매 공고 수집 스크립트

일정 API를 기반으로 최근 N일 내 공매 일정이 있는 공고만 수집합니다.

실행:
  python tests/test_collect_latest.py [days] [max_count]
  
  days: 최근 며칠 내 일정 조회 (기본: 180)
  max_count: 최대 수집 개수 (기본: 10)
  
예시:
  python tests/test_collect_latest.py
  python tests/test_collect_latest.py 365 20
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.kamco_collector_service import KamcoCollectorService


def collect_latest_announces(days=180, max_count=10, save_to_db=True):
    """
    최신 공매 공고 수집
    
    Args:
        days: 최근 며칠 내 일정 조회
        max_count: 최대 수집 개수
        save_to_db: MongoDB 저장 여부
    """
    print("=" * 100)
    print(f"최신 공매 공고 수집 (최근 {days}일)")
    print("=" * 100)
    print(f"수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"수집 개수: 최대 {max_count}건")
    print(f"MongoDB 저장: {'예' if save_to_db else '아니오'}")
    print()
    
    # 서비스 초기화
    service = KamcoCollectorService()
    
    # 1. 최근 일정 조회
    print(f"→ 최근 {days}일 공매 일정 조회 중...")
    
    import requests
    import xmltodict
    from urllib.parse import unquote
    
    # 날짜 범위
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    url = f"{service.base_url}/{service.service_path}/getKamcoPbctSchedule"
    params = {
        'serviceKey': service.service_key,
        'pageNo': 1,
        'numOfRows': max_count * 3,  # 중복 제거 후 max_count개 확보
        'PRPT_DVSN_CD': '0001',
        'STRT_DT': start_date.strftime('%Y%m%d'),
        'END_DT': today.strftime('%Y%m%d')
    }
    
    try:
        res = requests.get(url, params=params, headers=service.headers, timeout=service.timeout)
        res.raise_for_status()
        
        payload = xmltodict.parse(res.text)
        body = (payload.get('response') or {}).get('body') or {}
        items = body.get('items', {}).get('item', [])
        total = body.get('totalCount', 0)
        
        print(f"✅ 전체 {total}건의 일정 발견")
        
        if not items:
            print("⚠️  최근 일정이 없습니다.")
            return
        
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
                }
        
        announce_list = list(announces.values())[:max_count]
        print(f"✅ 중복 제거 후 {len(announce_list)}개 공고 발견")
        print()
        
    except Exception as e:
        print(f"❌ 일정 조회 실패: {e}")
        return
    
    # 2. 각 공고 상세 정보 수집
    print("=" * 100)
    print(f"공고 상세 정보 수집 시작")
    print("=" * 100)
    print()
    
    service.stats["total_announces"] = len(announce_list)
    
    collected_data = []
    
    for i, announce in enumerate(announce_list, 1):
        plnm_no = announce['PLNM_NO']
        pbct_no = announce['PBCT_NO']
        
        print(f"[{i}/{len(announce_list)}] 공고: {plnm_no}, 공매: {pbct_no}")
        print("-" * 80)
        
        try:
            # 공고 상세 정보 수집
            data = service.collect_announce_details(announce)
            
            if data:
                collected_data.append(data)
                service.stats["processed_announces"] += 1
                
                # 요약 출력
                plnm_nm = data.get('basic_info', {}).get('PLNM_NM', 'N/A')
                schedule_count = len(data.get('schedule_info', []))
                file_count = len(data.get('file_info', []))
                
                print(f"✅ {plnm_nm[:60]}")
                print(f"   일정: {schedule_count}개, 첨부파일: {file_count}개")
            else:
                service.stats["failed_announces"] += 1
                print("❌ 데이터 수집 실패")
                
        except Exception as e:
            service.stats["failed_announces"] += 1
            print(f"❌ 오류: {e}")
        
        print()
    
    # 3. MongoDB 저장
    if save_to_db and collected_data:
        print("=" * 100)
        print(f"MongoDB 저장 중 ({len(collected_data)}건)")
        print("=" * 100)
        print()
        
        if not service.client:
            service.connect_mongodb()
        
        for data in collected_data:
            try:
                service.save_to_mongodb(data)
                service.stats["saved_items"] += 1
            except Exception as e:
                print(f"❌ 저장 실패 (공고: {data.get('PLNM_NO')}): {e}")
        
        print(f"✅ {service.stats['saved_items']}건 저장 완료")
        print()
    
    # 4. 결과 요약
    print("=" * 100)
    print("수집 결과")
    print("=" * 100)
    print(f"전체 공고: {service.stats['total_announces']}건")
    print(f"처리 성공: {service.stats['processed_announces']}건")
    print(f"처리 실패: {service.stats['failed_announces']}건")
    if save_to_db:
        print(f"DB 저장: {service.stats['saved_items']}건")
    print()
    print(f"수집 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    collect_latest_announces(days=days, max_count=max_count, save_to_db=True)


if __name__ == "__main__":
    main()
