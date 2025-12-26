"""
PublicDataReader 라이브러리 종합 테스트

PublicDataReader를 사용한 한국자산관리공사(KAMCO) Open API 전체 기능 테스트

참고 문서:
- https://wooiljeong.github.io/python/pdr-kamco/

테스트 서비스:
1. 온비드코드조회서비스
2. 캠코공매물건조회서비스
3. 이용기관공매물건조회서비스
4. 정부재산정보공개조회서비스
5. 물건정보조회서비스

실행:
  pytest tests/test_publicdatareader_comprehensive.py -v
  또는
  python tests/test_publicdatareader_comprehensive.py
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
        pytest.skip("PublicDataReader가 설치되지 않았습니다. pip install PublicDataReader")
    
    service_key = os.getenv("KAMCO_SERVICE_KEY_DECODED") or os.getenv("KAMCO_SERVICE_KEY_ENCODED")
    if not service_key:
        pytest.skip("KAMCO_SERVICE_KEY가 설정되지 않았습니다.")
    
    # URL 디코딩
    if '%' in service_key:
        from urllib.parse import unquote
        service_key = unquote(service_key)
    
    return pdr.Kamco(service_key)


class TestPublicDataReaderInfo:
    """PublicDataReader 기본 정보 테스트"""
    
    def test_library_version(self):
        """라이브러리 버전 확인"""
        if not PDR_AVAILABLE:
            pytest.skip("PublicDataReader가 설치되지 않았습니다.")
        
        assert hasattr(pdr, '__version__')
        print(f"PublicDataReader version: {pdr.__version__}")
    
    def test_service_list(self, kamco_api):
        """사용 가능한 서비스 목록 확인"""
        assert hasattr(kamco_api, 'meta_dict')
        
        services = list(kamco_api.meta_dict.keys())
        print("\n사용 가능한 서비스:")
        for service in services:
            functions = list(kamco_api.meta_dict[service]['기능'].keys())
            print(f"  - {service}: {len(functions)}개 기능")
        
        # 필수 서비스 확인
        expected_services = [
            '온비드코드',
            '캠코공매물건',
            '이용기관공매물건',
            '정부재산정보공개',
            '물건정보'
        ]
        
        for service in expected_services:
            assert service in services, f"{service} 서비스가 없습니다."


class TestOnbidCode:
    """온비드코드조회서비스 테스트"""
    
    def test_용도상위코드(self, kamco_api):
        """용도 상위 코드 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="용도상위코드"
        )
        
        assert df is not None, "응답이 None입니다."
        assert len(df) > 0, "데이터가 없습니다."
        assert 'CTGR_ID' in df.columns
        assert 'CTGR_NM' in df.columns
        
        print(f"\n조회된 용도 상위 코드: {len(df)}개")
        print(df.head())
    
    def test_용도중간코드(self, kamco_api):
        """용도 중간 코드 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="용도중간코드",
            CTGR_ID="10000"  # 부동산
        )
        
        assert df is not None
        assert len(df) > 0
        assert 'CTGR_ID' in df.columns
        assert 'CTGR_HIRK_ID' in df.columns
        
        print(f"\n부동산 중간 코드: {len(df)}개")
        print(df.head())
    
    def test_용도하위코드(self, kamco_api):
        """용도 하위 코드 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="용도하위코드",
            CTGR_ID="10300"  # 상가용및업무용건물
        )
        
        assert df is not None
        assert len(df) > 0
        assert 'CTGR_ID' in df.columns
        assert 'CTGR_NM' in df.columns
        
        print(f"\n상가용 하위 코드: {len(df)}개")
        print(df.head())
    
    def test_시도(self, kamco_api):
        """시도 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="시도"
        )
        
        assert df is not None
        assert len(df) > 0
        assert 'ADDR1' in df.columns
        
        print(f"\n시도 목록: {len(df)}개")
        print(df.head())
        
        # 특정 시도가 포함되어 있는지 확인
        addr_list = df['ADDR1'].tolist()
        assert '서울특별시' in addr_list
        assert '경기도' in addr_list
    
    def test_시군구(self, kamco_api):
        """시군구 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="시군구",
            ADDR1="경기도"
        )
        
        assert df is not None
        assert len(df) > 0
        assert 'ADDR2' in df.columns
        
        print(f"\n경기도 시군구: {len(df)}개")
        print(df.head())
    
    def test_읍면동(self, kamco_api):
        """읍면동 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="읍면동",
            ADDR1="경기도",
            ADDR2="성남시 분당구"
        )
        
        assert df is not None
        assert len(df) > 0
        assert 'ADDR3' in df.columns
        
        print(f"\n성남시 분당구 읍면동: {len(df)}개")
        print(df.head())
    
    def test_상세주소(self, kamco_api):
        """상세주소 조회"""
        df = kamco_api.get_data(
            service="온비드코드",
            function="상세주소",
            ADDR3="정자동"
        )
        
        assert df is not None
        # 상세주소는 없을 수도 있음
        if len(df) > 0:
            assert 'DTL_ADDR' in df.columns
            print(f"\n정자동 상세주소: {len(df)}개")
            print(df.head())
        else:
            print("\n정자동 상세주소: 데이터 없음")


class TestKamcoAuction:
    """캠코공매물건조회서비스 테스트"""
    
    def test_물건목록(self, kamco_api):
        """캠코공매물건목록 조회"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="물건목록",
            DPSL_MTD_CD="0001",  # 매각
            CTGR_HIRK_ID="10000",  # 부동산
            CTGR_HIRK_ID_MID="10200",  # 주거용건물
            SIDO="서울특별시"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            assert 'CLTR_NM' in df.columns
            assert 'MIN_BID_PRC' in df.columns
            
            print(f"\n서울 주거용 물건: {len(df)}개")
            print(df.head())
        else:
            print("\n서울 주거용 물건: 데이터 없음")
    
    def test_공고목록(self, kamco_api):
        """캠코공매공고목록 조회"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="공고목록",
            PRPT_DVSN_CD="0001"  # 국유재산
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'PLNM_NO' in df.columns
            assert 'PBCT_NO' in df.columns
            assert 'PLNM_NM' in df.columns
            
            print(f"\n국유재산 공고: {len(df)}개")
            print(df.head())
        else:
            print("\n국유재산 공고: 데이터 없음")
    
    def test_일정(self, kamco_api):
        """캠코공매일정 조회"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="일정",
            PRPT_DVSN_CD="0001"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'PLNM_NO' in df.columns
            assert 'PBCT_BEGN_DTM' in df.columns
            assert 'PBCT_EXCT_DTM' in df.columns
            
            print(f"\n공매 일정: {len(df)}개")
            print(df.head())
        else:
            print("\n공매 일정: 데이터 없음")
    
    @pytest.mark.skip(reason="공고번호/공매번호가 필요하므로 선택적 실행")
    def test_공고기본정보(self, kamco_api):
        """캠코공매공고 기본정보 상세조회"""
        df = kamco_api.get_data(
            service="캠코공매물건",
            function="공고기본정보",
            PLNM_NO="697507",
            PBCT_NO="9677799"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'PLNM_NM' in df.columns
            assert 'ORG_NM' in df.columns
            print("\n공고 기본정보:")
            print(df.head())


class TestClientAuction:
    """이용기관공매물건조회서비스 테스트"""
    
    def test_공고목록(self, kamco_api):
        """이용기관 공고목록 조회"""
        df = kamco_api.get_data(
            service="이용기관공매물건",
            function="공고목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            CTGR_HIRK_ID_MID="10200",
            SIDO="경기도",
            SGK="성남시 분당구"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'PLNM_NO' in df.columns
            assert 'PLNM_NM' in df.columns
            
            print(f"\n성남시 분당구 공고: {len(df)}개")
            print(df.head())
        else:
            print("\n성남시 분당구 공고: 데이터 없음")
    
    def test_물건목록(self, kamco_api):
        """이용기관 물건목록 조회"""
        df = kamco_api.get_data(
            service="이용기관공매물건",
            function="물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            SIDO="경기도"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            assert 'CLTR_NM' in df.columns
            
            print(f"\n경기도 물건: {len(df)}개")
            print(df.head())
        else:
            print("\n경기도 물건: 데이터 없음")
    
    def test_통합공고목록(self, kamco_api):
        """이용기관 통합공고목록 조회"""
        df = kamco_api.get_data(
            service="이용기관공매물건",
            function="통합공고목록",
            DPSL_MTD_CD="0001",
            PLNM_KIND_CD="0001",
            CTGR_HIRK_ID="30000"
        )
        
        assert df is not None
        # 데이터가 없을 수도 있음
        print(f"\n통합공고목록: {len(df) if len(df) > 0 else 0}개")
    
    def test_매각공고목록(self, kamco_api):
        """이용기관 매각공고목록 조회"""
        df = kamco_api.get_data(
            service="이용기관공매물건",
            function="매각공고목록",
            PLNM_KIND_CD="0001",
            CTGR_HIRK_ID="10000"
        )
        
        assert df is not None
        print(f"\n매각공고목록: {len(df) if len(df) > 0 else 0}개")
    
    def test_임대공고목록(self, kamco_api):
        """이용기관 임대공고목록 조회"""
        df = kamco_api.get_data(
            service="이용기관공매물건",
            function="임대공고목록",
            PLNM_KIND_CD="0001",
            CTGR_HIRK_ID="10000"
        )
        
        assert df is not None
        print(f"\n임대공고목록: {len(df) if len(df) > 0 else 0}개")
    
    def test_마감임박공고목록(self, kamco_api):
        """이용기관 마감임박공고목록 조회"""
        df = kamco_api.get_data(
            service="이용기관공매물건",
            function="마감임박공고목록",
            DPSL_MTD_CD="0001",
            PLNM_KIND_CD="0001",
            CTGR_HIRK_ID="10000"
        )
        
        assert df is not None
        print(f"\n마감임박공고목록: {len(df) if len(df) > 0 else 0}개")


class TestGovernmentProperty:
    """정부재산정보공개조회서비스 테스트"""
    
    def test_정부재산정보공개정보목록(self, kamco_api):
        """정부재산정보공개 목록 조회"""
        df = kamco_api.get_data(
            service="정부재산정보공개",
            function="정부재산정보공개정보목록",
            CTGR_HIRK_ID="10000",
            SIDO="충청남도",
            SGK="태안군",
            EMD="고남면"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            assert 'CLTR_NM' in df.columns
            assert 'DLGT_ORG_NM' in df.columns
            
            print(f"\n태안군 고남면 정부재산: {len(df)}개")
            print(df.head())
        else:
            print("\n태안군 고남면 정부재산: 데이터 없음")
    
    @pytest.mark.skip(reason="물건번호가 필요하므로 선택적 실행")
    def test_정부재산정보공개정보상세(self, kamco_api):
        """정부재산정보공개 상세 조회"""
        df = kamco_api.get_data(
            service="정부재산정보공개",
            function="정부재산정보공개정보상세",
            CLTR_NO="3211132"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NM' in df.columns
            print("\n정부재산 상세정보:")
            print(df.head())
    
    def test_캠코관리재산정보공개목록정보(self, kamco_api):
        """캠코관리재산정보공개 목록 조회"""
        df = kamco_api.get_data(
            service="정부재산정보공개",
            function="캠코관리재산정보공개목록정보",
            CTGR_HIRK_ID="10000",
            SIDO="충청남도",
            SGK="태안군"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            print(f"\n태안군 캠코관리재산: {len(df)}개")
            print(df.head())
        else:
            print("\n태안군 캠코관리재산: 데이터 없음")


class TestItemInfo:
    """물건정보조회서비스 테스트"""
    
    def test_통합용도별물건목록(self, kamco_api):
        """통합용도별물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합용도별물건목록",
            CTGR_HIRK_ID="10000",
            SIDO="충청남도",
            SGK="태안군"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            assert 'CLTR_NM' in df.columns
            
            print(f"\n태안군 통합물건: {len(df)}개")
            print(df.head())
        else:
            print("\n태안군 통합물건: 데이터 없음")
    
    def test_통합새로운물건목록(self, kamco_api):
        """통합새로운물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합새로운물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            CTGR_HIRK_ID_MID="10200",
            SIDO="서울특별시"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            print(f"\n서울 새로운 물건: {len(df)}개")
            print(df.head())
        else:
            print("\n서울 새로운 물건: 데이터 없음")
    
    def test_통합마감임박물건목록(self, kamco_api):
        """통합마감임박물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합마감임박물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            CTGR_HIRK_ID_MID="10200",
            SIDO="충청남도"
        )
        
        assert df is not None
        print(f"\n충남 마감임박 물건: {len(df) if len(df) > 0 else 0}개")
    
    def test_통합수의계약가능물건목록(self, kamco_api):
        """통합수의계약가능물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합수의계약가능물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            CTGR_HIRK_ID_MID="10200",
            SIDO="서울특별시"
        )
        
        assert df is not None
        print(f"\n서울 수의계약가능 물건: {len(df) if len(df) > 0 else 0}개")
    
    def test_통합50퍼센트체감물건목록(self, kamco_api):
        """통합50%체감물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합50%체감물건목록",
            DPSL_MTD_CD="0001",
            CTGR_HIRK_ID="10000",
            CTGR_HIRK_ID_MID="10200",
            SIDO="서울특별시"
        )
        
        assert df is not None
        print(f"\n서울 50% 체감 물건: {len(df) if len(df) > 0 else 0}개")
    
    def test_통합클릭탑20물건목록(self, kamco_api):
        """통합클릭탑20물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합클릭탑20물건목록"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            print(f"\n클릭 TOP 20: {len(df)}개")
            print(df.head())
        else:
            print("\n클릭 TOP 20: 데이터 없음")
    
    def test_통합관심탑20물건목록(self, kamco_api):
        """통합관심탑20물건목록 조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합관심탑20물건목록"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NO' in df.columns
            print(f"\n관심 TOP 20: {len(df)}개")
            print(df.head())
        else:
            print("\n관심 TOP 20: 데이터 없음")


class TestItemDetailInfo:
    """물건정보 상세 조회 테스트"""
    
    @pytest.mark.skip(reason="물건번호/공매번호가 필요하므로 선택적 실행")
    def test_통합용도별물건기본정보상세(self, kamco_api):
        """통합용도별물건 기본정보 상세조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합용도별물건기본정보상세",
            CLTR_NO="1226758",
            PBCT_NO="9301922"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'CLTR_NM' in df.columns
            print("\n물건 기본정보:")
            print(df.head())
    
    @pytest.mark.skip(reason="물건번호/공매번호가 필요하므로 선택적 실행")
    def test_통합용도별물건감정평가서정보상세(self, kamco_api):
        """통합용도별물건 감정평가서정보 상세조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합용도별물건감정평가서정보상세",
            CLTR_NO="1226758",
            PBCT_NO="9301922"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'APSL_ASES_AMT' in df.columns
            print("\n감정평가 정보:")
            print(df.head())
    
    @pytest.mark.skip(reason="물건번호/공매번호가 필요하므로 선택적 실행")
    def test_통합용도별물건임대차정보상세(self, kamco_api):
        """통합용도별물건 임대차정보 상세조회"""
        df = kamco_api.get_data(
            service="물건정보",
            function="통합용도별물건임대차정보상세",
            CLTR_NO="1600012",
            PBCT_NO="9638282"
        )
        
        assert df is not None
        if len(df) > 0:
            assert 'IRST_DVSN_NM' in df.columns
            print("\n임대차 정보:")
            print(df.head())


# 메인 실행 함수
def main():
    """독립 실행을 위한 메인 함수"""
    if not PDR_AVAILABLE:
        print("❌ PublicDataReader가 설치되지 않았습니다.")
        print("   설치: pip install PublicDataReader pandas")
        return 1
    
    print("=" * 70)
    print("PublicDataReader 종합 테스트")
    print("=" * 70)
    
    # 서비스 키 확인
    service_key = os.getenv("KAMCO_SERVICE_KEY_DECODED") or os.getenv("KAMCO_SERVICE_KEY_ENCODED")
    if not service_key:
        print("❌ KAMCO_SERVICE_KEY가 설정되지 않았습니다.")
        return 1
    
    if '%' in service_key:
        from urllib.parse import unquote
        service_key = unquote(service_key)
    
    api = pdr.Kamco(service_key)
    
    # 1. 서비스 목록 출력
    print("\n[1] 사용 가능한 서비스 목록")
    print("-" * 70)
    for service, values in api.meta_dict.items():
        functions = list(values['기능'].keys())
        print(f"\n서비스: {service}")
        print(f"기능: {', '.join(functions[:5])}", end="")
        if len(functions) > 5:
            print(f" 외 {len(functions) - 5}개")
        else:
            print()
    
    # 2. 간단한 테스트 실행
    print("\n" + "=" * 70)
    print("[2] 샘플 데이터 조회")
    print("-" * 70)
    
    # 용도 상위 코드
    print("\n용도 상위 코드:")
    df = api.get_data(service="온비드코드", function="용도상위코드")
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print(df.head(3))
    else:
        print("  ❌ 조회 실패")
    
    # 시도 목록
    print("\n시도 목록:")
    df = api.get_data(service="온비드코드", function="시도")
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print(df.head(3))
    else:
        print("  ❌ 조회 실패")
    
    # 공고 목록
    print("\n최근 공고 목록 (국유재산):")
    df = api.get_data(service="캠코공매물건", function="공고목록", PRPT_DVSN_CD="0001")
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print(df.head(3))
    else:
        print("  ❌ 조회 실패 또는 데이터 없음")
    
    # 클릭 TOP 20
    print("\n클릭 TOP 20 물건:")
    df = api.get_data(service="물건정보", function="통합클릭탑20물건목록")
    if df is not None and len(df) > 0:
        print(f"  ✅ {len(df)}개 조회됨")
        print(df.head(3))
    else:
        print("  ❌ 조회 실패 또는 데이터 없음")
    
    print("\n" + "=" * 70)
    print("테스트 완료!")
    print("전체 테스트 실행: pytest tests/test_publicdatareader_comprehensive.py -v")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
