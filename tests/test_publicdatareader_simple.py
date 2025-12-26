"""
PublicDataReader 라이브러리 간단 테스트

실제 작동하는 API만 테스트합니다.

실행:
  pytest tests/test_publicdatareader_simple.py -v
  또는
  python tests/test_publicdatareader_simple.py
"""

import os
import sys
import pytest
from dotenv import load_dotenv

load_dotenv()

# PublicDataReader 설치 확인
try:
    import PublicDataReader as pdr
    import pandas as pd
    PDR_AVAILABLE = True
except ImportError:
    PDR_AVAILABLE = False


@pytest.fixture(scope="module")
def kamco_api():
    """KAMCO API 인스턴스 fixture"""
    if not PDR_AVAILABLE:
        pytest.skip("PublicDataReader가 설치되지 않았습니다.")
    
    service_key = os.getenv("KAMCO_SERVICE_KEY_DECODED") or os.getenv("KAMCO_SERVICE_KEY_ENCODED")
    if not service_key:
        pytest.skip("KAMCO_SERVICE_KEY가 설정되지 않았습니다.")
    
    if '%' in service_key:
        from urllib.parse import unquote
        service_key = unquote(service_key)
    
    return pdr.Kamco(service_key)


class TestBasicInfo:
    """기본 정보 테스트"""
    
    def test_library_available(self):
        """PublicDataReader 라이브러리 사용 가능 확인"""
        if not PDR_AVAILABLE:
            pytest.skip("PublicDataReader가 설치되지 않았습니다.")
        
        assert hasattr(pdr, '__version__')
        print(f"\n✅ PublicDataReader version: {pdr.__version__}")
    
    def test_service_list(self, kamco_api):
        """사용 가능한 서비스 목록 확인"""
        services = list(kamco_api.meta_dict.keys())
        
        print(f"\n✅ 사용 가능한 서비스: {len(services)}개")
        for service in services:
            functions = list(kamco_api.meta_dict[service]['기능'].keys())
            print(f"  • {service}: {len(functions)}개 기능")
        
        assert len(services) >= 5


class TestWorkingAPIs:
    """실제 작동하는 API 테스트"""
    
    def test_캠코공매물건_물건목록(self, kamco_api):
        """캠코공매물건 - 물건목록 조회 (한글 컬럼명)"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            SIDO="서울특별시"
        )
        
        assert df is not None
        assert len(df) > 0
        
        # PublicDataReader는 한글 컬럼명으로 변환
        assert '물건번호' in df.columns
        assert '물건명' in df.columns
        assert '최저입찰가' in df.columns
        
        print(f"\n✅ 캠코공매물건 물건목록: {len(df)}개 조회됨")
        print(f"   컬럼: {list(df.columns[:10])}")
        print(df.head(3))
    
    def test_캠코공매물건_공고목록(self, kamco_api):
        """캠코공매물건 - 공고목록 조회"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="공고목록",
            PRPT_DVSN_CD="0001"
        )
        
        assert df is not None
        assert len(df) > 0
        assert '공고번호' in df.columns
        assert '공고명' in df.columns
        
        print(f"\n✅ 캠코공매물건 공고목록: {len(df)}개 조회됨")
        print(df[['공고번호', '공고명', '공고일']].head(3))
    
    def test_캠코공매물건_일정(self, kamco_api):
        """캠코공매물건 - 일정 조회"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="일정",
            PRPT_DVSN_CD="0001"
        )
        
        assert df is not None
        assert len(df) > 0
        assert '공고번호' in df.columns
        assert '입찰시작일시' in df.columns
        assert '개찰일시' in df.columns
        
        print(f"\n✅ 캠코공매물건 일정: {len(df)}개 조회됨")
        print(df[['공고번호', '입찰시작일시', '개찰일시']].head(3))


class TestDataAnalysis:
    """데이터 분석 예시"""
    
    def test_price_analysis(self, kamco_api):
        """가격 분석 예시"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            SIDO="서울특별시"
        )
        
        if df is not None and len(df) > 0 and '최저입찰가' in df.columns:
            # 최저입찰가 컬럼이 있는 경우만 분석
            df_with_price = df[df['최저입찰가'].notna()].copy()
            
            if len(df_with_price) > 0:
                # 가격을 숫자로 변환
                df_with_price['최저입찰가'] = pd.to_numeric(df_with_price['최저입찰가'], errors='coerce')
                df_with_price = df_with_price[df_with_price['최저입찰가'] > 0].copy()
                
                if len(df_with_price) > 0:
                    # 가격 통계
                    print("\n✅ 가격 분석:")
                    print(f"   물건 수: {len(df_with_price)}개")
                    print(f"   최저입찰가 평균: {df_with_price['최저입찰가'].mean():,.0f}원")
                    print(f"   최저입찰가 최소: {df_with_price['최저입찰가'].min():,.0f}원")
                    print(f"   최저입찰가 최대: {df_with_price['최저입찰가'].max():,.0f}원")
                    
                    assert df_with_price['최저입찰가'].mean() > 0
    
    def test_date_analysis(self, kamco_api):
        """날짜 분석 예시"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="일정",
            PRPT_DVSN_CD="0001"
        )
        
        if df is not None and len(df) > 0:
            print("\n✅ 일정 분석:")
            print(f"   총 일정 수: {len(df)}개")
            
            # 최근 일정 확인
            if '입찰시작일시' in df.columns:
                recent = df.sort_values('입찰시작일시', ascending=False).head(5)
                print("\n   최근 5개 일정:")
                for idx, row in recent.iterrows():
                    print(f"   • {row['입찰시작일시']} ~ {row['개찰일시']}")


def main():
    """독립 실행"""
    if not PDR_AVAILABLE:
        print("❌ PublicDataReader가 설치되지 않았습니다.")
        print("   설치: pip install PublicDataReader pandas")
        return 1
    
    print("=" * 70)
    print("PublicDataReader 간단 테스트")
    print("=" * 70)
    
    service_key = os.getenv("KAMCO_SERVICE_KEY_DECODED") or os.getenv("KAMCO_SERVICE_KEY_ENCODED")
    if not service_key:
        print("❌ KAMCO_SERVICE_KEY가 설정되지 않았습니다.")
        return 1
    
    if '%' in service_key:
        from urllib.parse import unquote
        service_key = unquote(service_key)
    
    api = pdr.Kamco(service_key)
    
    # 1. 라이브러리 정보
    print(f"\n[1] PublicDataReader version: {pdr.__version__}")
    
    # 2. 서비스 목록
    print("\n[2] 사용 가능한 서비스:")
    for service, values in api.meta_dict.items():
        functions = list(values['기능'].keys())
        print(f"  • {service}: {len(functions)}개 기능")
    
    # 3. 실제 데이터 조회 테스트
    print("\n[3] 데이터 조회 테스트")
    print("-" * 70)
    
    # 공고 목록
    print("\n▶ 캠코공매물건 - 공고목록")
    df = api.get_data(service="캠코공매물건", function="공고목록", PRPT_DVSN_CD="0001")
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print(f"  컬럼: {list(df.columns)}")
        print("\n  샘플 데이터:")
        print(df[['공고번호', '공고명', '공고일']].head(3).to_string())
    else:
        print("  ❌ 조회 실패")
    
    # 물건 목록
    print("\n▶ 캠코공매물건 - 물건목록")
    df = api.get_data(
        service="캠코공매물건",
        function="물건목록",
        DPSL_MTD_CD="0001",
        CTGR_HIRK_ID="10000",
        SIDO="서울특별시"
    )
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print(f"  컬럼: {list(df.columns[:15])}")
        print("\n  샘플 데이터:")
        print(df[['물건번호', '물건명', '최저입찰가']].head(3).to_string())
    else:
        print("  ❌ 조회 실패")
    
    # 일정
    print("\n▶ 캠코공매물건 - 일정")
    df = api.get_data(service="캠코공매물건", function="일정", PRPT_DVSN_CD="0001")
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print("\n  최근 일정:")
        recent = df.sort_values('입찰시작일시', ascending=False).head(3)
        print(recent[['공고번호', '입찰시작일시', '개찰일시']].to_string())
    else:
        print("  ❌ 조회 실패")
    
    print("\n" + "=" * 70)
    print("✅ 테스트 완료!")
    print("pytest 실행: pytest tests/test_publicdatareader_simple.py -v")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
