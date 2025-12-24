# 캠코 API 테스트 - 실행 가능한 버전

## ✅ 작성 완료된 테스트 파일

다음 6개의 독립 실행 가능한 테스트 스크립트가 생성되었습니다:

1. **test_api_01_cltr_list.py** - 캠코공매물건목록조회
2. **test_api_02_announce_list.py** - 캠코공매공고목록조회  
3. **test_api_03_announce_basic.py** - 캠코공매공고 기본정보 상세조회
4. **test_api_04_schedule.py** - 캠코공매일정조회
5. **test_api_05_announce_schedule.py** - 캠코공매공고 공매일정 상세조회
6. **test_api_06_announce_file.py** - 캠코공매공고 첨부파일 상세조회

**전체 실행 스크립트:**
- **test_api_all.py** - 6가지 API를 순차적으로 모두 실행

## 📋 현재 상황

### 문제점
공공데이터포털에 명시된 서비스명(`KamcoAuctionInfoInquireSvc`)이 실제 API에서 동작하지 않습니다:
- 에러: `resultCode: 12, NO OPENAPI SERVICE ERROR`

### 동작하는 서비스
`test_api_simple.py`는 다른 서비스를 사용하여 정상 동작합니다:
- 서비스: `KamcoPblsalThingInquireSvc`
- Operation: `getKamcoPlnmPbctList`
- ✅ 정상 동작 확인됨

## 🔧 해결 방법

두 가지 옵션이 있습니다:

### 옵션 1: 실제 동작하는 서비스로 변경
`test_api_simple.py`처럼 실제로 동작하는 서비스 경로를 사용하도록 6개 테스트를 수정

### 옵션 2: 공공데이터포털 확인
공공데이터포털에서 실제 제공되는 API 명세와 서비스 경로를 다시 확인

## 📝 각 테스트 스크립트 실행 방법

```bash
# 개별 테스트 실행
python tests/test_api_01_cltr_list.py
python tests/test_api_02_announce_list.py
python tests/test_api_03_announce_basic.py
python tests/test_api_04_schedule.py
python tests/test_api_05_announce_schedule.py
python tests/test_api_06_announce_file.py

# 전체 테스트 실행
python tests/test_api_all.py
```

## 🔑 환경 설정

`.env` 파일에 다음 내용이 필요합니다:

```bash
KAMCO_SERVICE_KEY_ENCODED=your_api_key_here
# 또는
KAMCO_SERVICE_KEY_DECODED=your_api_key_here
```

## ✨ 주요 특징

- ✅ **이중 인코딩 방지**: API 키가 자동으로 디코딩되어 이중 인코딩 문제 해결
- ✅ **HTTP 사용**: HTTPS 대신 HTTP 사용 (온비드 API 권장사항)
- ✅ **브라우저 헤더**: 실제 브라우저처럼 헤더 설정
- ✅ **독립 실행**: pytest 없이 직접 실행 가능
- ✅ **상세한 출력**: API 요청/응답 상세 정보 출력
- ✅ **에러 처리**: 명확한 에러 메시지 제공

## 🚧 다음 단계

1. 공공데이터포털에서 실제 제공되는 서비스 목록 확인
2. 동작하는 서비스로 6개 테스트 스크립트 업데이트
3. 실제 API 호출 테스트 수행
