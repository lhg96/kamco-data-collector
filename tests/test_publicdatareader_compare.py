"""
PublicDataReader 라이브러리 vs 현재 구현 비교 테스트

PublicDataReader는 pandas DataFrame으로 데이터를 반환하는 편의 래퍼입니다.
현재 구현은 원본 XML/Dict 데이터를 직접 처리합니다.

실행:
  python tests/test_publicdatareader_compare.py

필요 패키지:
  pip install PublicDataReader pandas

참고:
  - https://github.com/WooilJeong/PublicDataReader
  - https://wooiljeong.github.io/python/pdr-kamco/
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_publicdatareader_available():
    """PublicDataReader 패키지 설치 확인"""
    try:
        import PublicDataReader as pdr
        print(f"✅ PublicDataReader version: {pdr.__version__}")
        return True
    except ImportError:
        print("❌ PublicDataReader가 설치되지 않았습니다.")
        print("   설치: pip install PublicDataReader pandas")
        return False


def test_current_implementation():
    """현재 구현 테스트"""
    print("\n" + "=" * 60)
    print("현재 구현 테스트 (KamcoCollectorService)")
    print("=" * 60)
    
    from services.kamco_collector_service import KamcoCollectorService
    
    service = KamcoCollectorService()
    
    # 1. 공고 목록 조회
    print("\n[1] 공고 목록 조회 (1개)")
    announces = service.fetch_announce_list(page_no=1, num_of_rows=1, prpt_dvsn_cd="0001")
    
    if announces:
        print(f"✅ 조회 성공: {len(announces)}개")
        first = announces[0]
        print(f"   공고번호: {first.get('PLNM_NO')}")
        print(f"   공매번호: {first.get('PBCT_NO')}")
        print(f"   공고명: {first.get('PLNM_NM', 'N/A')}")
        
        plnm_no = first.get('PLNM_NO')
        pbct_no = first.get('PBCT_NO')
        
        # 2. 기본정보 조회
        print("\n[2] 공고 기본정보 조회")
        basic_info = service.fetch_basic_info(plnm_no, pbct_no)
        if basic_info:
            print(f"✅ 조회 성공")
            print(f"   기관명: {basic_info.get('ORG_NM')}")
            print(f"   담당자: {basic_info.get('PSCG_NM')}")
        else:
            print("❌ 조회 실패")
        
        # 3. 첨부파일 조회
        print("\n[3] 첨부파일 조회")
        files = service.fetch_file_info(plnm_no, pbct_no)
        if files is not None:
            print(f"✅ 조회 성공: {len(files)}개")
            for i, f in enumerate(files[:3], 1):
                print(f"   {i}. {f.get('ATCH_FILE_NM')}")
        else:
            print("❌ 조회 실패")
        
        # 4. 일정 조회
        print("\n[4] 공매 일정 조회")
        schedules = service.fetch_schedule_info(plnm_no, pbct_no)
        if schedules is not None:
            print(f"✅ 조회 성공: {len(schedules)}개")
            for i, s in enumerate(schedules[:3], 1):
                print(f"   {i}. 입찰시작: {s.get('PBCT_BEGN_DTM')}")
        else:
            print("❌ 조회 실패")
        
        return True
    else:
        print("❌ 공고 목록 조회 실패")
        return False


def test_publicdatareader_kamco():
    """PublicDataReader 테스트"""
    print("\n" + "=" * 60)
    print("PublicDataReader 테스트")
    print("=" * 60)
    
    try:
        from PublicDataReader import Kamco
        import pandas as pd
        
        service_key = os.getenv("KAMCO_SERVICE_KEY_DECODED") or os.getenv("KAMCO_SERVICE_KEY_ENCODED")
        if not service_key:
            print("❌ KAMCO_SERVICE_KEY가 설정되지 않았습니다.")
            return False
        
        # URL 디코딩된 키 사용
        if '%' in service_key:
            from urllib.parse import unquote
            service_key = unquote(service_key)
        
        api = Kamco(service_key)
        
        # 1. 공고 목록 조회
        print("\n[1] 공고 목록 조회")
        df = api.get_data(
            service='캠코공매물건',
            function='공고목록',
            PRPT_DVSN_CD='0001'
        )
        
        if df is not None and len(df) > 0:
            print(f"✅ 조회 성공: {len(df)}개")
            print(f"   컬럼: {list(df.columns)[:10]}")
            print(f"\n   첫 번째 데이터:")
            first = df.iloc[0]
            print(f"   공고번호: {first.get('공고번호')}")
            print(f"   공매번호: {first.get('공매번호')}")
            print(f"   공고명: {first.get('공고명')}")
            
            # 2. 공고 기본정보 조회
            print("\n[2] 공고 기본정보 조회")
            try:
                df_basic = api.get_data(
                    service='캠코공매물건',
                    function='공고기본정보',
                    PLNM_NO=str(first.get('공고번호')),
                    PBCT_NO=str(first.get('공매번호'))
                )
                
                if df_basic is not None and len(df_basic) > 0:
                    print(f"✅ 조회 성공")
                    print(f"   기관명: {df_basic.iloc[0].get('공고기관')}")
                    print(f"   담당자: {df_basic.iloc[0].get('담당자명')}")
                else:
                    print("❌ 데이터 없음")
            except Exception as e:
                print(f"❌ 오류: {e}")
            
            # 3. 첨부파일 조회
            print("\n[3] 첨부파일 조회")
            try:
                df_files = api.get_data(
                    service='캠코공매물건',
                    function='공고첨부파일',
                    PLNM_NO=str(first.get('공고번호')),
                    PBCT_NO=str(first.get('공매번호'))
                )
                
                if df_files is not None and len(df_files) > 0:
                    print(f"✅ 조회 성공: {len(df_files)}개")
                    for i, row in df_files.head(3).iterrows():
                        print(f"   {i+1}. {row.get('첨부파일명')}")
                else:
                    print("⚠️ 첨부파일 없음")
            except Exception as e:
                print(f"⚠️ {e}")
            
            # 4. 일정 조회
            print("\n[4] 공매 일정 조회")
            try:
                df_schedule = api.get_data(
                    service='캠코공매물건',
                    function='공고공매일정',
                    PLNM_NO=str(first.get('공고번호')),
                    PBCT_NO=str(first.get('공매번호'))
                )
                
                if df_schedule is not None and len(df_schedule) > 0:
                    print(f"✅ 조회 성공: {len(df_schedule)}개")
                    for i, row in df_schedule.head(3).iterrows():
                        print(f"   {i+1}. 입찰시작: {row.get('입찰시작일시')}")
                else:
                    print("⚠️ 일정 없음")
            except Exception as e:
                print(f"⚠️ {e}")
            
            return True
        else:
            print("❌ 공고 목록 조회 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_features():
    """기능 비교"""
    print("\n" + "=" * 60)
    print("기능 비교")
    print("=" * 60)
    
    print("\n[PublicDataReader]")
    print("  장점:")
    print("    ✅ pandas DataFrame 형식으로 반환 (데이터 분석 편리)")
    print("    ✅ 컬럼명이 한글로 자동 변환")
    print("    ✅ pip install로 간편 설치")
    print("    ✅ 여러 API 통합 (KAMCO, 국세청, KB부동산 등)")
    print("  단점:")
    print("    ❌ 원본 데이터 구조 접근 어려움")
    print("    ❌ 외부 패키지 의존성")
    
    print("\n[현재 구현 (KamcoCollectorService)]")
    print("  장점:")
    print("    ✅ 원본 XML/Dict 데이터 직접 처리")
    print("    ✅ MongoDB 저장 기능 내장")
    print("    ✅ Flask 웹 UI 통합")
    print("    ✅ 중복 제거 로직")
    print("    ✅ 외부 의존성 최소화")
    print("  단점:")
    print("    ❌ 데이터 분석 시 추가 처리 필요")
    print("    ❌ 컬럼명이 영문 약자")


def main():
    """메인 함수"""
    print("=" * 60)
    print("KAMCO API 구현 비교 테스트")
    print("PublicDataReader vs KamcoCollectorService")
    print("=" * 60)
    
    # 1. 현재 구현 테스트
    current_result = test_current_implementation()
    
    # 2. PublicDataReader 테스트
    if test_publicdatareader_available():
        pdr_result = test_publicdatareader_kamco()
    else:
        pdr_result = False
    
    # 3. 기능 비교
    compare_features()
    
    # 4. 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"현재 구현: {'✅ 성공' if current_result else '❌ 실패'}")
    print(f"PublicDataReader: {'✅ 성공' if pdr_result else '⚠️ 미설치 또는 실패'}")
    
    print("\n[권장사항]")
    print("  • 데이터 수집 & 저장: 현재 구현 사용")
    print("  • 데이터 분석: PublicDataReader 사용 고려")
    print("  • 웹 UI: 현재 구현 계속 사용")
    
    return 0 if current_result else 1


if __name__ == "__main__":
    sys.exit(main())
