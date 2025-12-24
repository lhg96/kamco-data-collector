"""
KAMCO 공매 데이터 수집 서비스 테스트

실행:
  python tests/test_kamco_collector_service.py

환경변수 (.env):
  KAMCO_SERVICE_KEY_ENCODED - KAMCO API 키
  MONGO_URI - MongoDB 연결 URI (기본값: mongodb://localhost:27017)
  TEST_PLNM_NO - 첨부파일 테스트용 공고번호 (기본값: 464351)
  TEST_PBCT_NO - 첨부파일 테스트용 공매번호 (기본값: 9314139)
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from services.kamco_collector_service import KamcoCollectorService

load_dotenv()


def test_service_initialization():
    """서비스 초기화 테스트"""
    print("=" * 80)
    print("1. 서비스 초기화 테스트")
    print("=" * 80)
    
    try:
        service = KamcoCollectorService(
            db_name="kamco",
            collection_name="test_collected_items"
        )
        print("✅ 서비스 초기화 성공")
        print(f"   API Base URL: {service.base_url}")
        print(f"   Service Path: {service.service_path}")
        print(f"   MongoDB URI: {service.mongo_uri}")
        print(f"   DB Name: {service.db_name}")
        print(f"   Collection: {service.collection_name}")
        return service
    except Exception as e:
        print(f"❌ 서비스 초기화 실패: {e}")
        return None


def test_mongodb_connection(service: KamcoCollectorService):
    """MongoDB 연결 테스트"""
    print("\n" + "=" * 80)
    print("2. MongoDB 연결 테스트")
    print("=" * 80)
    
    if service.connect_mongodb():
        print("✅ MongoDB 연결 성공")
        service.close_mongodb()
        return True
    else:
        print("❌ MongoDB 연결 실패")
        return False


def test_fetch_announce_list(service: KamcoCollectorService):
    """공고 목록 조회 테스트"""
    print("\n" + "=" * 80)
    print("3. 공고 목록 조회 테스트")
    print("=" * 80)
    
    announces = service.fetch_announce_list(page_no=1, num_of_rows=3)
    
    if announces is None:
        print("❌ 공고 목록 조회 실패")
        return None
    
    if not announces:
        print("⚠️  조회된 공고가 없습니다")
        return None
    
    print(f"✅ 공고 목록 조회 성공: {len(announces)}개")
    
    # 첫 번째 공고 정보 출력
    first = announces[0]
    print(f"\n첫 번째 공고:")
    print(f"   PLNM_NO: {first.get('PLNM_NO', 'N/A')}")
    print(f"   PBCT_NO: {first.get('PBCT_NO', 'N/A')}")
    print(f"   PLNM_NM: {first.get('PLNM_NM', 'N/A')}")
    
    return announces


def test_fetch_basic_info(service: KamcoCollectorService, plnm_no: str, pbct_no: str):
    """기본 정보 조회 테스트"""
    print("\n" + "=" * 80)
    print("4. 기본 정보 조회 테스트")
    print("=" * 80)
    print(f"PLNM_NO: {plnm_no}, PBCT_NO: {pbct_no}")
    
    basic_info = service.fetch_basic_info(plnm_no, pbct_no)
    
    if basic_info:
        print("✅ 기본 정보 조회 성공")
        print(f"   공고명: {basic_info.get('PLNM_NM', 'N/A')}")
        print(f"   기관명: {basic_info.get('ORG_NM', 'N/A')}")
        print(f"   담당부서: {basic_info.get('RSBY_DEPT', 'N/A')}")
        return True
    else:
        print("⚠️  기본 정보 없음")
        return False


def test_fetch_schedule_info(service: KamcoCollectorService, plnm_no: str, pbct_no: str):
    """일정 정보 조회 테스트"""
    print("\n" + "=" * 80)
    print("5. 일정 정보 조회 테스트")
    print("=" * 80)
    print(f"PLNM_NO: {plnm_no}, PBCT_NO: {pbct_no}")
    
    schedule_info = service.fetch_schedule_info(plnm_no, pbct_no)
    
    if schedule_info is None:
        print("❌ 일정 정보 조회 실패")
        return False
    
    if not schedule_info:
        print("⚠️  일정 정보 없음")
        return True
    
    print(f"✅ 일정 정보 조회 성공: {len(schedule_info)}개")
    first = schedule_info[0]
    print(f"   공매번호: {first.get('PBCT_NO', 'N/A')}")
    print(f"   공매차수: {first.get('PBCT_DGR', 'N/A')}")
    print(f"   입찰방식: {first.get('BID_DVSN_NM', 'N/A')}")
    return True


def test_fetch_file_info(service: KamcoCollectorService):
    """첨부 파일 정보 조회 테스트"""
    print("\n" + "=" * 80)
    print("6. 첨부 파일 정보 조회 테스트")
    print("=" * 80)
    
    # 첨부파일이 있는 공고로 테스트
    test_plnm_no = os.getenv("TEST_PLNM_NO", "464351")
    test_pbct_no = os.getenv("TEST_PBCT_NO", "9314139")
    
    print(f"→ 첨부파일 테스트용 공고 사용")
    print(f"   PLNM_NO: {test_plnm_no}, PBCT_NO: {test_pbct_no}")
    
    file_info = service.fetch_file_info(test_plnm_no, test_pbct_no)
    
    if file_info is None:
        print("❌ 첨부 파일 정보 조회 실패")
        return False
    
    if not file_info:
        print("⚠️  첨부 파일 없음")
        return True
    
    print(f"✅ 첨부 파일 정보 조회 성공: {len(file_info)}개")
    
    # 첨부파일 목록 출력
    print(f"\n   첨부파일 목록:")
    for idx, file in enumerate(file_info, 1):
        print(f"      [{idx}] {file.get('ATCH_FILE_NM', 'N/A')}")
        print(f"          파일번호: {file.get('ATCH_FILE_PTCS_NO', 'N/A')}")
        print(f"          경로: {file.get('FILE_PTH_CNTN', 'N/A')}")
    
    return True


def test_collect_announce_details(service: KamcoCollectorService, announce: dict):
    """공고 상세 정보 수집 테스트"""
    print("\n" + "=" * 80)
    print("7. 공고 상세 정보 수집 테스트")
    print("=" * 80)
    
    # 먼저 첨부파일이 있는 공고로 테스트
    test_plnm_no = os.getenv("TEST_PLNM_NO", "464351")
    test_pbct_no = os.getenv("TEST_PBCT_NO", "9314139")
    
    print(f"→ 첨부파일이 있는 공고로 테스트")
    print(f"   PLNM_NO: {test_plnm_no}, PBCT_NO: {test_pbct_no}")
    
    test_announce = {
        "PLNM_NO": test_plnm_no,
        "PBCT_NO": test_pbct_no,
        "PLNM_NM": "첨부파일 테스트용 공고"
    }
    
    collected_with_files = service.collect_announce_details(test_announce)
    
    if collected_with_files:
        print("✅ 첨부파일 있는 공고 수집 성공")
        print(f"   PLNM_NO: {collected_with_files['PLNM_NO']}")
        print(f"   PBCT_NO: {collected_with_files['PBCT_NO']}")
        print(f"   기본 정보: {'있음' if collected_with_files['basic_info'] else '없음'}")
        print(f"   일정 정보: {len(collected_with_files['schedule_info'])}개")
        print(f"   첨부 파일: {len(collected_with_files['file_info'])}개")
        
        if collected_with_files['file_info']:
            print(f"\n   첨부파일 목록:")
            for idx, file in enumerate(collected_with_files['file_info'], 1):
                print(f"      [{idx}] {file.get('ATCH_FILE_NM', 'N/A')}")
    
    # 원래 공고도 테스트
    print(f"\n→ 원래 공고 테스트")
    collected = service.collect_announce_details(announce)
    
    if not collected:
        print("❌ 상세 정보 수집 실패")
        return None
    
    print("✅ 상세 정보 수집 성공")
    print(f"   PLNM_NO: {collected['PLNM_NO']}")
    print(f"   PBCT_NO: {collected['PBCT_NO']}")
    print(f"   기본 정보: {'있음' if collected['basic_info'] else '없음'}")
    print(f"   일정 정보: {len(collected['schedule_info'])}개")
    print(f"   첨부 파일: {len(collected['file_info'])}개")
    print(f"   수집 시간: {collected['collected_at']}")
    
    return collected


def test_full_collection_with_db(service: KamcoCollectorService):
    """전체 수집 프로세스 테스트 (MongoDB 저장 포함)"""
    print("\n" + "=" * 80)
    print("8. 전체 수집 프로세스 테스트 (MongoDB 저장)")
    print("=" * 80)
    
    stats = service.run(
        page_no=1,
        num_of_rows=2,  # 테스트용으로 2개만
        prpt_dvsn_cd="0001",
        save_to_db=True,
    )
    
    print("\n최종 통계:")
    print(f"   전체 공고: {stats['total_announces']}개")
    print(f"   처리 성공: {stats['processed_announces']}개")
    print(f"   처리 실패: {stats['failed_announces']}개")
    print(f"   DB 저장: {stats['saved_items']}개")
    
    return stats


def main():
    print("=" * 80)
    print("KAMCO 공매 데이터 수집 서비스 테스트")
    print("=" * 80)
    print()
    
    # 1. 서비스 초기화
    service = test_service_initialization()
    if not service:
        return 1
    
    # 2. MongoDB 연결 테스트
    if not test_mongodb_connection(service):
        print("\n⚠️  MongoDB 연결 실패 - DB 저장 테스트는 건너뜁니다")
        # MongoDB 없이도 계속 진행
    
    # 3. 공고 목록 조회
    announces = test_fetch_announce_list(service)
    if not announces:
        return 2
    
    # 첫 번째 공고로 상세 테스트
    first_announce = announces[0]
    plnm_no = first_announce.get("PLNM_NO")
    pbct_no = first_announce.get("PBCT_NO")
    
    # 4. 기본 정보 조회
    test_fetch_basic_info(service, plnm_no, pbct_no)
    
    # 5. 일정 정보 조회
    test_fetch_schedule_info(service, plnm_no, pbct_no)
    
    # 6. 첨부 파일 정보 조회 (첨부파일이 있는 공고로)
    test_fetch_file_info(service)
    
    # 7. 상세 정보 수집 (첨부파일 있는 공고 + 원래 공고)
    test_collect_announce_details(service, first_announce)
    
    # 8. 전체 수집 프로세스 (MongoDB 저장)
    test_full_collection_with_db(service)
    
    print("\n" + "=" * 80)
    print("🎉 모든 테스트가 완료되었습니다!")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
