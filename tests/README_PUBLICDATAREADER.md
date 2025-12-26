# PublicDataReader 테스트 가이드

## 개요

PublicDataReader는 한국자산관리공사(KAMCO)를 포함한 다양한 공공 데이터 API를 쉽게 사용할 수 있게 해주는 Python 라이브러리입니다.

## 설치

```bash
pip install PublicDataReader pandas
```

또는 프로젝트 전체 패키지 설치:

```bash
pip install -r requirements.txt
```

## 테스트 파일

### 1. test_publicdatareader_comprehensive.py

**전체 기능 종합 테스트**

PublicDataReader의 모든 KAMCO API 기능을 테스트합니다:

- ✅ 온비드코드조회서비스 (7개 기능)
- ✅ 캠코공매물건조회서비스 (6개 기능)
- ✅ 이용기관공매물건조회서비스 (6개 기능)
- ✅ 정부재산정보공개조회서비스 (4개 기능)
- ✅ 물건정보조회서비스 (15개 기능)

**실행 방법:**

```bash
# pytest로 전체 테스트 실행
pytest tests/test_publicdatareader_comprehensive.py -v

# pytest로 특정 테스트 클래스만 실행
pytest tests/test_publicdatareader_comprehensive.py::TestOnbidCode -v

# pytest로 특정 테스트만 실행
pytest tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_용도상위코드 -v

# 독립 실행 (간단한 샘플 테스트)
python tests/test_publicdatareader_comprehensive.py
```

### 2. test_publicdatareader_compare.py

**PublicDataReader vs 현재 구현 비교 테스트**

두 가지 접근 방식을 비교합니다:
- PublicDataReader: pandas DataFrame으로 반환
- KamcoCollectorService: 원본 XML/Dict 데이터 처리

**실행 방법:**

```bash
python tests/test_publicdatareader_compare.py
```

## 테스트 대상 서비스

### 1. 온비드코드조회서비스

물건 분류 코드와 주소 정보를 조회합니다.

```python
import PublicDataReader as pdr

api = pdr.Kamco(serviceKey)

# 용도 상위 코드 조회
df = api.get_data(service="온비드코드", function="용도상위코드")

# 용도 중간 코드 조회
df = api.get_data(service="온비드코드", function="용도중간코드", CTGR_ID="10000")

# 시도 조회
df = api.get_data(service="온비드코드", function="시도")

# 시군구 조회
df = api.get_data(service="온비드코드", function="시군구", ADDR1="경기도")

# 읍면동 조회
df = api.get_data(service="온비드코드", function="읍면동", 
                  ADDR1="경기도", ADDR2="성남시 분당구")
```

### 2. 캠코공매물건조회서비스

캠코 공매 물건과 공고 정보를 조회합니다.

```python
# 물건 목록 조회
df = api.get_data(
    service="캠코공매물건",
    function="물건목록",
    DPSL_MTD_CD="0001",  # 매각
    CTGR_HIRK_ID="10000",  # 부동산
    CTGR_HIRK_ID_MID="10200",  # 주거용건물
    SIDO="서울특별시"
)

# 공고 목록 조회
df = api.get_data(
    service="캠코공매물건",
    function="공고목록",
    PRPT_DVSN_CD="0001"  # 국유재산
)

# 일정 조회
df = api.get_data(
    service="캠코공매물건",
    function="일정",
    PRPT_DVSN_CD="0001"
)
```

### 3. 이용기관공매물건조회서비스

이용기관이 등록한 공매 물건을 조회합니다.

```python
# 공고 목록 조회
df = api.get_data(
    service="이용기관공매물건",
    function="공고목록",
    DPSL_MTD_CD="0001",
    CTGR_HIRK_ID="10000",
    SIDO="경기도",
    SGK="성남시 분당구"
)

# 마감임박 공고 조회
df = api.get_data(
    service="이용기관공매물건",
    function="마감임박공고목록",
    DPSL_MTD_CD="0001",
    PLNM_KIND_CD="0001",
    CTGR_HIRK_ID="10000"
)
```

### 4. 정부재산정보공개조회서비스

정부 소유 재산 정보를 조회합니다.

```python
# 정부재산 목록 조회
df = api.get_data(
    service="정부재산정보공개",
    function="정부재산정보공개정보목록",
    CTGR_HIRK_ID="10000",
    SIDO="충청남도",
    SGK="태안군",
    EMD="고남면"
)

# 캠코관리재산 목록 조회
df = api.get_data(
    service="정부재산정보공개",
    function="캠코관리재산정보공개목록정보",
    CTGR_HIRK_ID="10000",
    SIDO="충청남도",
    SGK="태안군"
)
```

### 5. 물건정보조회서비스

통합 물건 정보와 상세 정보를 조회합니다.

```python
# 통합용도별 물건 목록
df = api.get_data(
    service="물건정보",
    function="통합용도별물건목록",
    CTGR_HIRK_ID="10000",
    SIDO="충청남도",
    SGK="태안군"
)

# 새로운 물건 목록
df = api.get_data(
    service="물건정보",
    function="통합새로운물건목록",
    DPSL_MTD_CD="0001",
    CTGR_HIRK_ID="10000",
    CTGR_HIRK_ID_MID="10200",
    SIDO="서울특별시"
)

# 클릭 TOP 20
df = api.get_data(
    service="물건정보",
    function="통합클릭탑20물건목록"
)

# 관심 TOP 20
df = api.get_data(
    service="물건정보",
    function="통합관심탑20물건목록"
)
```

## 환경 설정

테스트 실행 전에 `.env` 파일에 KAMCO 서비스 키를 설정해야 합니다:

```bash
KAMCO_SERVICE_KEY_DECODED=your_service_key_here
```

또는

```bash
KAMCO_SERVICE_KEY_ENCODED=your_encoded_service_key_here
```

## 주요 파라미터

### 처분방법코드 (DPSL_MTD_CD)
- `0001`: 매각
- `0002`: 임대(대부)

### 재산구분코드 (PRPT_DVSN_CD)
- `0001`: 국유재산
- `0002`: 공유재산
- `0004`: 불용품
- `0005`: 기타일반재산
- `0008`: 수탁재산(캠코)

### 용도계층코드 (CTGR_HIRK_ID)
- `10000`: 부동산
- `11000`: 권리/증권
- `12000`: 자동차/운송장비
- `13000`: 농/임/축산업
- `14000`: 어업
- `30000`: 재활용품

### 용도중간코드 (CTGR_HIRK_ID_MID) - 부동산
- `10100`: 토지
- `10200`: 주거용건물
- `10300`: 상가용및업무용건물
- `10400`: 산업용및기타특수용건물
- `10500`: 용도복합용건물
- `10600`: 미분류건물

### 공고종류코드 (PLNM_KIND_CD)
- `0001`: 일반공고
- `0002`: 정정공고
- `0003`: 수정공고
- `0004`: 취소공고

## 테스트 결과 예시

```bash
$ pytest tests/test_publicdatareader_comprehensive.py -v

tests/test_publicdatareader_comprehensive.py::TestPublicDataReaderInfo::test_library_version PASSED
tests/test_publicdatareader_comprehensive.py::TestPublicDataReaderInfo::test_service_list PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_용도상위코드 PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_용도중간코드 PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_용도하위코드 PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_시도 PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_시군구 PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_읍면동 PASSED
tests/test_publicdatareader_comprehensive.py::TestOnbidCode::test_상세주소 PASSED
...

============================== 38 passed in 45.23s ==============================
```

## 장단점 비교

### PublicDataReader 장점
✅ pandas DataFrame으로 반환되어 데이터 분석 편리  
✅ 컬럼명이 한글로 자동 변환  
✅ pip install로 간편 설치  
✅ 여러 공공 API 통합 지원  

### PublicDataReader 단점
❌ 원본 데이터 구조 접근 어려움  
❌ 외부 패키지 의존성  

### KamcoCollectorService 장점
✅ 원본 XML/Dict 데이터 직접 처리  
✅ MongoDB 저장 기능 내장  
✅ Flask 웹 UI 통합  
✅ 중복 제거 로직  
✅ 외부 의존성 최소화  

### KamcoCollectorService 단점
❌ 데이터 분석 시 추가 처리 필요  
❌ 컬럼명이 영문 약자  

## 권장 사항

- **데이터 수집 & 저장**: KamcoCollectorService 사용
- **데이터 분석**: PublicDataReader 사용 고려
- **웹 UI**: KamcoCollectorService 계속 사용
- **탐색적 데이터 분석**: PublicDataReader + Jupyter Notebook

## 참고 자료

- [PublicDataReader GitHub](https://github.com/WooilJeong/PublicDataReader)
- [PublicDataReader KAMCO 가이드](https://wooiljeong.github.io/python/pdr-kamco/)
- [공공데이터포털](https://www.data.go.kr/)
- [온비드](https://www.onbid.co.kr/)

## 트러블슈팅

### ImportError: No module named 'PublicDataReader'

```bash
pip install PublicDataReader pandas
```

### 서비스 키 오류

`.env` 파일에 올바른 서비스 키가 설정되어 있는지 확인하세요.

### 데이터가 없음 (빈 DataFrame)

특정 검색 조건에 해당하는 데이터가 없을 수 있습니다. 검색 조건을 완화하거나 다른 지역/조건으로 시도해보세요.

### API 호출 제한

공공데이터포털 API는 호출 횟수 제한이 있을 수 있습니다. 너무 많은 요청을 짧은 시간에 보내지 않도록 주의하세요.
