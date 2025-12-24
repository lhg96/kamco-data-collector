# 캠코 API 테스트 코드 생성 완료 ✅

## 생성된 테스트 파일 목록

### 캠코공매물건조회서비스 (KamcoAuctionInfoInquireSvc) - 6개 파일

1. **test_kamco_cltr_list.py** 
   - API: `getKamcoAuctionCltrList` (캠코공매물건목록조회)
   - 파라미터: serviceKey, pageNo, numOfRows
   - 기능: 캠코에서 공매하는 물건 목록을 조회

2. **test_kamco_announce_list.py**
   - API: `getKamcoAuctionAnnounceList` (캠코공매공고목록조회)
   - 파라미터: serviceKey, pageNo, numOfRows
   - 기능: 공매 공고 목록을 조회

3. **test_kamco_announce_basic.py**
   - API: `getKamcoAuctionAnnounceBasicInfo` (캠코공매공고 기본정보 상세조회)
   - 파라미터: serviceKey, pblancNo
   - 기능: 특정 공고의 기본 정보를 상세 조회

4. **test_kamco_schedule.py**
   - API: `getKamcoAuctionScheduleList` (캠코공매일정조회)
   - 파라미터: serviceKey, pageNo, numOfRows
   - 기능: 공매 일정 목록을 조회

5. **test_kamco_announce_schedule.py**
   - API: `getKamcoAuctionAnnounceScheduleDetail` (캠코공매공고 공매일정 상세조회)
   - 파라미터: serviceKey, pblancNo, pbctSn
   - 기능: 특정 공고의 공매 일정 상세 정보 조회

6. **test_kamco_announce_file.py**
   - API: `getKamcoAuctionAnnounceFileDetail` (캠코공매공고 첨부파일 상세조회)
   - 파라미터: serviceKey, pblancNo
   - 기능: 공고에 첨부된 파일 정보 조회

### 물건정보조회서비스 (ThingInfoInquireSvc) - 2개 파일

7. **test_thing_usage_cltr.py**
   - API: `getUnifyUsageCltr` (통합용도별물건목록조회)
   - 파라미터: serviceKey, pageNo, numOfRows
   - 기능: 용도별로 물건 목록을 조회

8. **test_thing_usage_details.py** (8개 API 포함)
   - `getUnifyUsageCltrBasicInfoDetail` - 기본정보 상세조회
   - `getUnifyUsageCltrEstimationInfoDetail` - 감정평가서정보 상세조회
   - `getUnifyUsageCltrRentalInfoDetail` - 임대차정보 상세조회
   - `getUnifyUsageCltrRegisteredInfoDetail` - 권리종류정보 상세조회
   - `getUnifyUsageCltrBidDateInfoDetail` - 공매일정 상세조회
   - `getUnifyUsageCltrBidHistoryInfoDetail` - 입찰이력 상세조회
   - `getUnifyUsageCltrStockholderInfoDetail` - 주주정보 상세조회
   - `getUnifyUsageCltrCorporatebodyInfoDetail` - 법인현황정보 상세조회
   - 파라미터: serviceKey, cltrMnmtNo

### 문서 파일

9. **README_API_TESTS.md**
   - 모든 테스트 사용법 및 API 상세 정보
   - 환경 설정 가이드
   - 문제 해결 방법

## 테스트 실행 방법

### 1. 기본 테스트 (Mock 데이터, API 호출 없음)
```bash
pytest tests/test_kamco_*.py tests/test_thing_*.py -v
```

### 2. 통합 테스트 (실제 API 호출)
```bash
RUN_INTEGRATION=1 pytest tests/test_kamco_*.py tests/test_thing_*.py -v
```

### 3. 특정 테스트만 실행
```bash
# 캠코공매물건목록조회만 테스트
pytest tests/test_kamco_cltr_list.py -v

# 통합용도별물건 관련 테스트
pytest tests/test_thing_*.py -v

# 파싱 테스트만 (API 호출 없음)
pytest tests/ -v -k "parse"
```

## 테스트 구조

각 테스트 파일은 다음 2가지 테스트를 포함합니다:

1. **실제 API 호출 테스트**
   - `RUN_INTEGRATION=1` 환경변수 설정 시에만 실행
   - 실제 API 엔드포인트를 호출하여 응답 검증
   - API 키 필요

2. **응답 파싱 테스트**
   - 항상 실행됨 (API 호출 없음)
   - Mock XML 데이터를 사용하여 파싱 로직 검증
   - API 키 불필요

## 필수 환경 설정

`.env` 파일에 다음 값들을 설정하세요:

```bash
# 필수: 공공데이터포털에서 발급받은 URL-Encoded API 키
KAMCO_SERVICE_KEY_ENCODED=your_encoded_key_here

# 선택: 상세조회 테스트용 (실제 값으로 변경)
TEST_PBLANC_NO=202412-001           # 공고번호
TEST_PBCT_SN=1                       # 공매일련번호
TEST_CLTR_MNMT_NO=202412-001-001    # 물건관리번호
```

## 테스트 결과

```bash
$ pytest tests/test_kamco_*.py tests/test_thing_*.py -v

================================ test session starts =================================
collected 23 items                                                                   

tests/test_kamco_announce_basic.py::test_get_kamco_auction_announce_basic_info SKIPPED
tests/test_kamco_announce_basic.py::test_parse_announce_basic_info_response PASSED
tests/test_kamco_announce_file.py::test_get_kamco_auction_announce_file_detail SKIPPED
tests/test_kamco_announce_file.py::test_parse_announce_file_detail_response PASSED
tests/test_kamco_announce_list.py::test_get_kamco_auction_announce_list SKIPPED
tests/test_kamco_announce_list.py::test_parse_announce_list_response PASSED
tests/test_kamco_announce_schedule.py::test_get_kamco_auction_announce_schedule_detail SKIPPED
tests/test_kamco_announce_schedule.py::test_parse_announce_schedule_detail_response PASSED
tests/test_kamco_cltr_list.py::test_get_kamco_auction_cltr_list SKIPPED
tests/test_kamco_cltr_list.py::test_parse_cltr_list_response PASSED
tests/test_kamco_schedule.py::test_get_kamco_auction_schedule_list SKIPPED
tests/test_kamco_schedule.py::test_parse_schedule_list_response PASSED
tests/test_thing_usage_cltr.py::test_get_unify_usage_cltr SKIPPED
tests/test_thing_usage_cltr.py::test_parse_unify_usage_cltr_response PASSED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_basic_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_estimation_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_rental_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_registered_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_bid_date_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_bid_history_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_stockholder_info_detail SKIPPED
tests/test_thing_usage_details.py::test_get_unify_usage_cltr_corporatebody_info_detail SKIPPED
tests/test_thing_usage_details.py::test_parse_basic_info_response PASSED

=========================== 8 passed, 15 skipped in 0.04s ============================
```

## 주요 특징

✅ **14개 API 엔드포인트** 커버  
✅ **23개 테스트 케이스** 포함  
✅ **실제 API 호출 + Mock 테스트** 병행  
✅ **자세한 문서화** (README 포함)  
✅ **환경변수 기반** 설정 (API 키, 테스트 파라미터)  
✅ **pytest 표준** 사용  

## 참고사항

- 모든 테스트는 공공데이터포털의 캠코 온비드 OpenAPI를 기반으로 합니다
- 실제 API 호출 테스트는 API 키가 필요하며, 활용신청 승인이 완료되어야 합니다
- Mock 테스트는 API 키 없이도 실행 가능합니다
- 상세조회 API는 실제 존재하는 ID/번호가 필요합니다 (환경변수로 설정)
