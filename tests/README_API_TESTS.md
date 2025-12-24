# 캠코(KAMCO) API 테스트 코드

공공데이터포털의 캠코 온비드(Onbid) OpenAPI를 테스트하는 코드 모음입니다.

## 📋 테스트 파일 목록

### 1. KamcoPblsalThingInquireSvc (캠코공매물건조회서비스)

| 파일명 | API 명 | 설명 |
|--------|--------|------|
| `test_api_01_cltr_list.py` | getKamcoPbctCltrList | 캠코공매물건목록조회 |
| `test_api_02_announce_list.py` | getKamcoPlnmPbctList | 캠코공매공고목록조회 |
| `test_api_03_announce_basic.py` | getKamcoPlnmPbctBasicInfoDetail | 캠코공매공고 기본정보 상세조회 |
| `test_api_04_schedule.py` | getKamcoPbctSchedule | 캠코공매일정조회 |
| `test_api_05_announce_schedule.py` | getKamcoPlnmPbctBidDateInfoDetail | 캠코공매공고 공매일정 상세조회 |
| `test_api_06_announce_file.py` | getKamcoPlnmPbctFileInfoDetail | 캠코공매공고 첨부파일 상세조회 |

### 2. 통합 테스트

| 파일명 | 설명 |
|--------|------|
| `test_api_all.py` | 6개 API 전체를 순차적으로 실행하는 통합 테스트 스크립트 |
| `test_api_simple.py` | API 키 검증 및 간단한 연결 테스트 |

### 3. 기타 테스트 (pytest 기반)

| 파일명 | 설명 |
|--------|------|
| `test_api_cli.py` | FastAPI `/ask` 엔드포인트 통합 테스트 |
| `test_api_rag.py` | RAG 시스템 관련 테스트 |
| `test_embed.py` | 임베딩 기능 테스트 |
| `test_fetcher.py` | 데이터 수집 기능 테스트 |
| `test_normalizer.py` | 데이터 정규화 기능 테스트 |

## 🚀 사용법
LNM_NO=464351      # 공고번호
TEST_PBCT_NO=9314139     # 공매번호
```

### 2. 개별 API 테스트 실행

각 API를 독립적으로 실행할 수 있습니다:

```bash
# 1. 캠코공매물건목록조회
python tests/test_api_01_cltr_list.py

# 2. 캠코공매공고목록조회
python tests/test_api_02_announce_list.py

# 3. 캠코공매공고 기본정보 상세조회
python tests/test_api_03_announce_basic.py

# 4. 캠코공매일정조회
python tests/test_api_04_schedule.py

# 5. 캠코공매공고 공매일정 상세조회
python tests/test_api_05_announce_schedule.py

# 6. 캠코공매공고 첨부파일 상세조회
python tests/test_api_06_announce_file.py
```

### 3. 전체 API 테스트 실행

모든 API를 순차적으로 테스트합니다:

```bash
# 전체 6개 API 통합 테스트
python tests/test_api_all.py
```

### 4. pytest 기반 테스트 실행

기타 테스트는 pytest로 실행합니다:

```bash
# FastAPI 통합 테스트 (서버 실행 필요)
RUN_INTEGRATION=1 pytest tests/test_api_cli.py -v

# RAG, 임베딩 등 기능 테스트
pytest tests/test_api_rag.py -v
pytest tests/test_embed.py -v
```

## 📝 테스트 구조

### 독립 실행 스크립트 (test_api_01~06, test_api_all)

- Python 스크립트로 직접 실행 (`python tests/test_api_XX.py`)
- 실제 API를 호출하여 응답 검증
- 컬러 출력으로 결과 표시
- `.env` 파일에서 자동으로 환경변수 로드

### pytest 기반 테스트

- `pytest` 명령으로 실행
- Mock 데이터 또는 실제 API 호출 (환경변수에 따라)
- 단위 테스트 및 통합 테스트 포함 """실제 API를 호출하여 응답을 검증"""
    # RUN_INTEGRATION=1 환경변수가 설정되어야 실행됨
```

### 2. 응답 파싱 테스트

```python
def test_parse_cltr_list_response():
    """Mock XML 응답을 파싱하여 데이터 구조 검증"""
    # 항상 실행됨 (API 호출 없음)
```

## 🔍 API 상세 정보

###PLNM_NO`: 공고번호 (공고 상세조회 시 필요)
- `PBCT_NO`: 공매번호 (공매일정/첨부파일 상세조회 시 필요)
- `DPSL_MTD_CD`: 처분방법코드 (물건목록조회 시 선택)
- `PRPT_DVSN_CD`: 재산구분코드 (공고목록/일정조회 시 선택ncoded 키
- `pageNo`: 페이지 번호 (기본값: 1)
- `numOfRows`: 한 페이지당 조회 건수 (기본값: 10)
### 개별 API 실행 결과

```bash
$ python tests/test_api_01_cltr_list.py

→ GET http://openapi.onbid.co.kr/openapi/services/KamcoPblsalThingInquireSvc/getKamcoPbctCltrList
   params: pageNo=1, numOfRows=10, DPSL_MTD_CD=0001
   resultCode: 00
   resultMsg: NORMAL SERVICE.
✅ 캠코공매물건목록조회 성공: 10개 조회 (전체: 74629)

첫 번째 물건 정보:
   RNUM: 1
   PLNM_NO: 842356
   PBCT_NO: 9970473
   ...
```

### 전체 API 통합 실행 결과

```bash
$ python tests/test_api_all.py

================================================================================
캠코 6가지 API 전체 테스트 시작
================================================================================

[1. 캠코공_SERVICE_KEY_ENCODED is not set in .env
```

→ `.env` 파일에 `KAMCO_SERVICE_KEY_ENCODED` 설정 확인

### 인증 오류 (resultCode=12)

```
❌ API error: resultCode=12 - NO OPENAPI SERVICE ERROR
```

→ 서비스 경로가 올바른지 확인 (`KamcoPblsalThingInquireSvc` 사용)
→ API 키가 이중 인코딩되지 않았는지 확인 (자동 처리됨)

### 연결 오류

```
❌ Request failed: HTTPSConnectionPool...
```

→ HTTP 프로토콜 사용 확인 (HTTPS 아님)
→ 네트워크 연결 상태 확인

### 데이터 없음 (resultCode=00, 데이터 없음
tests/test_kamco_cltr_list.py::test_parse_cltr_list_response PASSED   [100%]
✅ 캠코공매물건목록 응답 파싱 성공

====== 2 passed in 1.23s ======
```

## 🛠️ 문제 해결

### API 키 오류

```
❌ KAMCO service key not set
```

→ `.env` 파일에 `KAMCO_SERVICE_KEY_ENCODED` 설정 확인

### 인증 오류 (resultCode=30, 31, 32, 33)

```
❌ API error: resultCode=30 - SERVICE_KEY_IS_NOT_REGISTERED_ERROR
```

→ API 키가 올바르게 URL-Encoded 되었는지 확인
→ 공공데이터포털에서 해당 API 활용신청 승인 여부 확인

### 데이터 없음 (resultCode=03)

```
✅ API 호출 성공 (데이터 없음)
```

→ 정상적인 응답입니다. 조회 조건에 맞는 데이터가 없을 때 발생합니다.

## 📚 참고 자료

- [공공데이터포털](https://www.data.go.kr/)
- [캠코 온비드 공식 사이트](https://www.onbid.co.kr/)
- API 문서: 공공데이터포털에서 각 API 활용신청 후 확인 가능

## 📄 라이선스

이 테스트 코드는 캠코 공공 API의 사용 예시를 제공하기 위한 것이며, 실제 API 사용시 공공데이터포털의 이용약관을 준수해야 합니다.
