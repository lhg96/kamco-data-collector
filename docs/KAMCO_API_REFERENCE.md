# KAMCO OpenAPI 개발자 가이드 v1.2

## 📋 목차
1. [API 개요](#api-개요)
2. [인증 및 접근](#인증-및-접근)
3. [API 목록](#api-목록)
4. [상세 API 명세](#상세-api-명세)
5. [오류 코드](#오류-코드)
6. [구현 상태](#구현-상태)
7. [사용 예제](#사용-예제)

---

## API 개요

### 서비스 정보
- **서비스명**: 물건정보조회서비스 (KamcoPblsalThingInquireSvc)
- **Base URL**: `http://openapi.onbid.co.kr/openapi/services/`
- **프로토콜**: REST (GET)
- **응답 형식**: XML
- **버전**: 1.2
- **문의**: 공공데이터운영센터 / 051-794-4588

### 기술 사양
- **프로토콜**: HTTP (HTTPS 타임아웃 문제로 HTTP 권장)
- **인증 방식**: Service Key (URL 인코딩)
- **요청 제한**: 40 TPS
- **응답 시간**: 최대 600ms
- **최대 요청 크기**: 6000 bytes

---

## 인증 및 접근

### Service Key 처리
```python
# Service Key는 URL 인코딩되어 제공됨
# 중복 디코딩 방지 필요!

def _normalize_service_key(key: str) -> str:
    """Service key 정규화 (중복 디코딩 방지)"""
    decoded_once = unquote(key)
    decoded_twice = unquote(decoded_once)
    return decoded_twice if decoded_twice != decoded_once else decoded_once
```

### 환경 변수 설정
```bash
# .env 파일
KAMCO_API_KEY=your_service_key_here
```

---

## API 목록

KAMCO OpenAPI는 총 **15개의 오퍼레이션**을 제공합니다:

### 물건 목록 조회 APIs (1-7)

| No | API 명칭 | Operation Name | 설명 | 구현 |
|----|---------|----------------|------|------|
| 1 | 통합용도물건목록 | `getUnifyUsageCltr` | 전체 통합 용도별 물건 목록 | ✅ |
| 2 | 통합신규물건목록 | `getUnifyNewCltrList` | 등록 후 1개월 이내 신규 물건 | ✅ |
| 3 | 통합마감임박물건목록 | `getUnifyDeadlineCltrList` | 입찰 마감 48시간 이내 | ✅ |
| 4 | 통합수의계약물건목록 | `getUnifyPrivateContractCltrList` | 수의계약 대상 물건 | ✅ |
| 5 | 통합50%인하물건목록 | `getUnifyDegression50PerCltrList` | 50% 이상 인하된 물건 | ✅ |
| 6 | 통합조회상위20물건목록 | `getUnifyClickTop20CltrList` | 조회수 상위 20건 | ✅ |
| 7 | 통합관심상위20물건목록 | `getUnifyInterestTop20CltrList` | 관심물건 상위 20건 | ❌ |

### 물건 상세정보 APIs (8-15)

| No | API 명칭 | Operation Name | 설명 | 구현 |
|----|---------|----------------|------|------|
| 8 | 통합용도물건기본정보 | `getUnifyUsageCltrBasicInfoDetail` | 물건 기본정보 | ✅ |
| 9 | 통합용도물건감정평가정보 | `getUnifyUsageCltrEstimationInfoDetail` | 감정평가 정보 | ❌ |
| 10 | 통합용도물건임대차정보 | `getUnifyUsageCltrRentalInfoDetail` | 임대차 정보 | ❌ |
| 11 | 통합용도물건등기사항정보 | `getUnifyUsageCltrRegisteredInfoDetail` | 등기사항 정보 | ❌ |
| 12 | 통합용도물건입찰일정정보 | `getUnifyUsageCltrBidDateInfoDetail` | 입찰일정 정보 | ✅ |
| 13 | 통합용도물건입찰이력정보 | `getUnifyUsageCltrBidHistoryInfoDetail` | 입찰이력 정보 | ❌ |
| 14 | 통합용도물건주주정보 | `getUnifyUsageCltrStockholderInfoDetail` | 주주정보 (주식용) | ❌ |
| 15 | 통합용도물건법인재무정보 | `getUnifyUsageCltrCorporatebodyInfoDetail` | 법인재무정보 | ❌ |

### 추가 API (공고 및 파일)

| API | 설명 | 구현 |
|-----|------|------|
| `getKamcoPlnmPbctList` | 공고목록 조회 | ✅ |
| `getKamcoPlnmPbctBasicInfoDetail` | 공고 기본정보 | ✅ |
| `getKamcoPbctSchedule` | 일정조회 (최신 공고용) | ✅ |
| `getKamcoPlnmPbctBidDateInfoDetail` | 공고 일정상세 | ✅ |
| `getKamcoPlnmPbctFileInfoDetail` | 첨부파일 정보 | ✅ |

---

## 상세 API 명세

### 1. getUnifyUsageCltr - 통합용도물건목록조회

**용도**: 전체 통합 용도별 물건 검색 (부동산, 자동차, 기계, 주식 등)

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 (URL 인코딩) | - |
| numOfRows | Integer | ✓ | 한 페이지 결과 수 | 10 |
| pageNo | Integer | ✓ | 페이지 번호 | 1 |
| DPSL_MTD_CD | String(4) | ○ | 처분방법 (0001:매각, 0002:임대) | 0001 |
| CTGR_HIRK_ID | String(20) | ○ | 분류체계ID (상위) | 30100 |
| CTGR_HIRK_ID_MID | String(20) | ○ | 분류체계ID (중위) | 10100 |
| SIDO | String(100) | ○ | 시도명 (서울특별시) | 서울특별시 |
| SGK | String(100) | ○ | 시군구명 | 강남구 |
| EMD | String(100) | ○ | 읍면동명 | 역삼동 |
| GOODS_PRICE_FROM | Number(20) | ○ | 감정가 최소 | 10000000 |
| GOODS_PRICE_TO | Number(20) | ○ | 감정가 최대 | 50000000 |
| OPEN_PRICE_FROM | Number(20) | ○ | 최저입찰가 최소 | 5000000 |
| OPEN_PRICE_TO | Number(20) | ○ | 최저입찰가 최대 | 30000000 |
| CLTR_NM | String(500) | ○ | 물건명 | 아파트 |
| PBCT_BEGN_DTM | String(8) | ○ | 입찰기간 From (YYYYMMDD) | 20240101 |
| PBCT_CLS_DTM | String(8) | ○ | 입찰기간 To (YYYYMMDD) | 20241231 |
| ORG_NM | String(100) | ○ | 기관명 | 한국자산관리공사 |
| ORG_BASE_NO | String(10) | ○ | 기관코드 | 10000 |
| CLTR_MNMT_NO | String(50) | ○ | 물건관리번호 | 2024-00001 |

#### Response Fields (주요)
| 필드 | 타입 | 설명 |
|------|------|------|
| PLNM_NO | Number(22) | 공고번호 |
| PBCT_NO | Number(22) | 공매번호 |
| CLTR_NO | Number(22) | 물건번호 |
| CLTR_NM | String(1000) | 물건명 |
| LDNM_ADRS | String(1000) | 지번주소 |
| NMRD_ADRS | String(1000) | 도로명주소 |
| MIN_BID_PRC | String(20) | 최저입찰가 |
| APSL_ASES_AVG_AMT | String(20) | 감정평가금액 |
| PBCT_BEGN_DTM | String(14) | 입찰시작일시 (YYYYMMDDHH24MISS) |
| PBCT_CLS_DTM | String(14) | 입찰종료일시 |
| PBCT_CLTR_STAT_NM | String(100) | 물건상태 |
| DPSL_MTD_NM | String(100) | 처분방법명 |
| BID_MTD_NM | String(100) | 입찰방법명 |

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyUsageCltr
```

---

### 2. getUnifyNewCltrList - 신규물건목록조회

**용도**: 등록일 기준 1개월 이내 신규 물건 조회

#### 주요 차이점
- 공고 등록일 기준 최근 1개월 이내 물건만 반환
- 파라미터는 `getUnifyUsageCltr`와 동일

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyNewCltrList
```

---

### 3. getUnifyDeadlineCltrList - 마감임박물건목록조회

**용도**: 입찰 마감 48시간 이내 물건 조회

#### 주요 차이점
- 입찰종료일시 기준 48시간 이내 물건만 반환

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyDeadlineCltrList
```

---

### 4. getUnifyPrivateContractCltrList - 수의계약물건목록조회

**용도**: 수의계약 대상 물건 조회 (공개입찰 유찰 후 수의계약 전환)

#### 입찰방법
- 수의계약 (Private Contract)
- 매각기관이 직접 가격 협상

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyPrivateContractCltrList
```

---

### 5. getUnifyDegression50PerCltrList - 50%인하물건목록조회

**용도**: 최저입찰가가 감정평가금액 대비 50% 이하로 인하된 물건

#### 주요 특징
- 유찰 횟수가 많아 가격이 크게 하락한 물건
- 투자 기회 물건 발굴

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyDegression50PerCltrList
```

---

### 6. getUnifyClickTop20CltrList - 조회수상위20물건목록조회

**용도**: 조회수 기준 상위 20개 물건 (인기물건)

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 | 값 |
|------|------|------|------|-----|
| CTGR_TYPE_ID | String(4) | ○ | 물건카테고리 | 0001: 부동산<br>0002: 자동차/운수기계<br>0003: 기계(공작)<br>0004: 기계(기타)<br>0005: 유체/채권 |

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyClickTop20CltrList
```

---

### 8. getUnifyUsageCltrBasicInfoDetail - 물건기본정보상세조회

**용도**: 특정 물건의 상세 기본정보 조회

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 |
| CLTR_NO | Number(22) | ✓ | 물건번호 |
| PBCT_NO | Number(22) | ✓ | 공매번호 |

#### Response Fields (물건 유형별)

##### 공통 필드
| 필드 | 타입 | 설명 |
|------|------|------|
| CLTR_NM | String(1000) | 물건명 |
| CTGR_TYPE_NM | String(100) | 물건카테고리 (부동산/자동차/기계/주식) |
| DPSL_MTD_NM | String(100) | 처분방법명 |
| PBCT_CLTR_STAT_NM | String(100) | 물건상태 |
| ORG_NM | String(100) | 입찰주최기관 |
| RGST_DEPT_NM | String(100) | 부서명 |
| PSCG_NM | String(100) | 담당자명 |
| PSCG_TPNO | String(50) | 전화번호 |
| LDNM_ADRS | String(1000) | 지번주소 |
| NMRD_ADRS | String(1000) | 도로명주소 |
| CLTR_MNMT_NO | String(50) | 물건관리번호 |
| PRPT_DVSN_NM | String(100) | 재산구분 |
| BID_MTD_NM | String(100) | 입찰방법명 |
| MIN_BID_PRC | Number(22) | 입찰시작가 |

##### 부동산 전용 필드
| 필드 | 타입 | 설명 |
|------|------|------|
| LAND_SQMS | String(50) | 토지면적 |
| BLD_SQMS | String(50) | 건물면적 |
| BLD_NM | String(200) | 건물명 |
| DONG | String(50) | 동 |
| FLR | String(50) | 층 |
| HOUS | String(50) | 호 |
| POSI_ENV_PSCD | String(500) | 위치환경특기사항 |
| UTLZ_PSCD | String(2000) | 이용특기사항 |
| ESCT_YN | String(1) | 에스컬레이터여부 |
| ELVT_YN | String(1) | 엘리베이터여부 |
| SHR_YN | String(1) | 공유여부 |
| PKLT_YN | String(1) | 주차장여부 |

##### 자동차 전용 필드
| 필드 | 타입 | 설명 |
|------|------|------|
| MANF | String(200) | 제조사 |
| MDL | String(500) | 모델명 |
| NRGT | String(4) | 연식 |
| VHKN | String(500) | 차종 |
| VHC_NO | String(2000) | 차량번호 |
| VHCL_MLGE | Number(22) | 주행거리 (km) |
| GRBX | String(200) | 변속기 |
| ENDPC | Number(22) | 배기량 (cc) |
| FUEL | String(200) | 연료 |
| CSTD_PLC | String(500) | 보관장소 |

##### 기계 전용 필드
| 필드 | 타입 | 설명 |
|------|------|------|
| MANF | String(200) | 제조사명 |
| MDL | String(500) | 모델명 |
| NRGT | String(4) | 제조년도 |
| STND | String(500) | 규격 |
| PSNS_SIZE | String(200) | 본선 |
| PRDN_PLC_CTFR | String(50) | 생산국가코드 |
| USE_TERM | Number(22) | 사용기간 |
| WGHT_QNTY | String(100) | 무게 |
| QNTY | Number(22) | 수량 |

##### 주식/채권 전용 필드
| 필드 | 타입 | 설명 |
|------|------|------|
| SCRT_NM | String(500) | 채권명 |
| MBS_SCRT_NO | String(2000) | 회사채권번호 |
| MMB_RGT_NM | String(200) | 회사채명 |
| QNTY | Number(22) | 수량 (주) |
| PCOS | Number(22) | 공유비율 |
| STK_PER_DNMT_PRC | Number(22) | 주당액면가 |
| DNMT_TOT_AMT | Number(22) | 액면총액 |
| ISU_STK_TOT_CNT | Number(22) | 발행주식총수 |

#### Response - 하위 상세정보 카운트
| 필드 | 설명 |
|------|------|
| totalCountEst | 감정평가정보 개수 |
| totalCountRental | 임대차정보 개수 |
| totalCountRegi | 등기사항정보 개수 |
| totalCountBid | 입찰일정 개수 |
| totalCountBidHis | 입찰이력 개수 |
| totalCountStock | 주주정보 개수 (주식용) |
| totalCountCorpor | 법인재무정보 개수 |

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyUsageCltrBasicInfoDetail
```

---

### 12. getUnifyUsageCltrBidDateInfoDetail - 입찰일정정보조회

**용도**: 물건의 입찰 회차별 일정 정보

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 |
| CLTR_NO | Number(22) | ✓ | 물건번호 |
| PBCT_NO | Number(22) | ✓ | 공매번호 |
| numOfRows | Integer | ✓ | 페이지당 결과 수 |
| pageNo | Integer | ✓ | 페이지 번호 |

#### Response Fields
| 필드 | 타입 | 설명 |
|------|------|------|
| BID_MNMT_NO | String(50) | 입찰코드 |
| PBCT_SEQ | String(3) | 회차 |
| PBCT_DGR | String(5) | 차수 |
| BID_DVSN_NM | String(100) | 입찰구분명 |
| PCMT_PYMT_MTD_CNTN | String(400) | 보증금납부방법 |
| PCMT_PYMT_EPDT_CNTN | String(400) | 보증금납부기한 |
| PBCT_BEGN_DTM | String(14) | 입찰시작일시 |
| PBCT_CLS_DTM | String(14) | 입찰종료일시 |
| PBCT_EXCT_DTM | String(14) | 개찰일시 |
| OPBD_PLC_CNTN | String(14) | 개찰장소 |
| DPSL_DCSN_DTM | String(14) | 매각결정일시 |
| MIN_BID_PRC | String(24) | 최저입찰가 |

#### API 엔드포인트
```
GET /openapi/services/ThingInfoInquireSvc/getUnifyUsageCltrBidDateInfoDetail
```

---

### 추가 구현 API (공고 조회)

### getKamcoPlnmPbctList - 공고목록조회

**용도**: 공고 목록 조회 (정렬되지 않음 - 최신 데이터 보장 안 됨)

#### ⚠️ 중요 사항
- **이 API는 정렬되지 않은 데이터를 반환합니다**
- 2024년 공고와 2018년 공고가 섞여 반환될 수 있음
- **최신 공고 조회는 `getKamcoPbctSchedule` 사용 권장**

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 |
| numOfRows | Integer | ✓ | 페이지당 결과 수 |
| pageNo | Integer | ✓ | 페이지 번호 |
| SEARCH_TYPE | String | ○ | 검색타입 (PLNM_NO, PBCT_NO 등) |
| SEARCH_KEYWORD | String | ○ | 검색어 |

#### Response Fields
| 필드 | 타입 | 설명 |
|------|------|------|
| PLNM_NO | String | 공고번호 |
| PBCT_NO | String | 공매번호 |
| PLNM_NM | String | 공고명 |
| PLNM_CLTR_CNT | Number | 공고물건수 |
| PLNM_RGST_DT | String(8) | 공고등록일 (YYYYMMDD) |
| PBCT_BEGN_DTM | String(14) | 입찰시작일시 |
| PBCT_CLS_DTM | String(14) | 입찰종료일시 |

---

### getKamcoPlnmPbctBasicInfoDetail - 공고기본정보상세

**용도**: 공고의 상세 기본정보 조회

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 |
| PLNM_NO | String | ✓ | 공고번호 |
| PBCT_NO | String | ✓ | 공매번호 |

#### Response Structure
```xml
<response>
  <body>
    <item>
      <!-- 기본정보 -->
    </item>
  </body>
</response>
```

#### ⚠️ 응답 구조 주의사항
- **응답은 `body.item`에 있습니다** (NOT `body.items.item`)
- 다른 목록 API들과 구조가 다름

---

### getKamcoPbctSchedule - 일정조회 (⭐ 최신 공고 조회 권장)

**용도**: 일정 기준 최신 공고 조회 - **신뢰할 수 있는 최신 데이터**

#### 왜 이 API를 사용해야 하는가?
1. ✅ **일정 기준 정렬**: 입찰일정 기준으로 정렬된 데이터 반환
2. ✅ **최신 데이터 보장**: 최근 N일 기준 조회 가능
3. ✅ **날짜 필터링**: 시작일/종료일 지정 가능

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 |
| numOfRows | Integer | ✓ | 페이지당 결과 수 |
| pageNo | Integer | ✓ | 페이지 번호 |
| SEARCH_START_DATE | String(8) | ○ | 검색시작일 (YYYYMMDD) |
| SEARCH_END_DATE | String(8) | ○ | 검색종료일 (YYYYMMDD) |

#### Response Fields
| 필드 | 타입 | 설명 |
|------|------|------|
| PLNM_NO | String | 공고번호 |
| PBCT_NO | String | 공매번호 |
| PBCT_BEGN_DTM | String(14) | 입찰시작일시 |
| PBCT_CLS_DTM | String(14) | 입찰종료일시 |
| CLTR_CNT | Number | 물건수 |

#### 사용 예제 (최신 7일 공고)
```python
from datetime import datetime, timedelta

# 최근 7일 기준
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

params = {
    'serviceKey': api_key,
    'numOfRows': 100,
    'pageNo': 1,
    'SEARCH_START_DATE': start_date.strftime('%Y%m%d'),
    'SEARCH_END_DATE': end_date.strftime('%Y%m%d')
}
```

---

### getKamcoPlnmPbctFileInfoDetail - 첨부파일정보조회

**용도**: 공고/물건의 첨부파일 목록 조회

#### Request Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| serviceKey | String | ✓ | API 인증키 |
| PLNM_NO | String | ✓ | 공고번호 |
| PBCT_NO | String | ✓ | 공매번호 |
| CLTR_NO | String | ○ | 물건번호 (선택) |

#### Response Fields
| 필드 | 타입 | 설명 |
|------|------|------|
| ATCH_FILE_PTCS_NO | String | 첨부파일일련번호 (중복 제거 키) |
| ATCH_FILE_NM | String | 파일명 |
| ATCH_FILE_URL | String | 다운로드 URL |
| ATCH_FILE_SIZE | Number | 파일크기 (bytes) |

#### ⚠️ 중복 제거
- 같은 파일이 여러 물건에 중복 첨부될 수 있음
- `ATCH_FILE_PTCS_NO`로 중복 제거 필요

```python
# 중복 제거 로직
unique_files = {}
for file in files:
    file_id = file.get("ATCH_FILE_PTCS_NO")
    if file_id and file_id not in unique_files:
        unique_files[file_id] = file

deduplicated = list(unique_files.values())
```

---

## 오류 코드

### HTTP 응답 코드
| 코드 | 설명 |
|------|------|
| 200 | 정상 처리 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 존재하지 않는 리소스 |
| 500 | 서버 오류 |

### API resultCode (response.header.resultCode)
| 코드 | resultMsg | 설명 |
|------|-----------|------|
| 00 | NORMAL_CODE | 정상 |
| 01 | APPLICATION_ERROR | 어플리케이션 에러 |
| 02 | DB_ERROR | 데이터베이스 에러 |
| 03 | NODATA_ERROR | 데이터없음 에러 |
| 04 | HTTP_ERROR | HTTP 에러 |
| 05 | SERVICETIMEOUT_ERROR | 서비스 연결실패 에러 |
| 10 | INVALID_REQUEST_PARAMETER_ERROR | 잘못된 요청 파라미터 에러 |
| 11 | NO_MANDATORY_REQUEST_PARAMETERS_ERROR | 필수요청 파라미터가 없음 |
| 12 | NO_OPENAPI_SERVICE_ERROR | 해당 오픈API서비스가 없거나 폐기됨 |
| 20 | SERVICE_ACCESS_DENIED_ERROR | 서비스 접근거부 |
| 21 | TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR | 일시적으로 사용할 수 없는 서비스키 |
| 22 | LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR | 서비스 요청제한횟수 초과에러 |
| 30 | SERVICE_KEY_IS_NOT_REGISTERED_ERROR | 등록되지 않은 서비스키 |
| 31 | DEADLINE_HAS_EXPIRED_ERROR | 기한만료된 서비스키 |
| 32 | UNREGISTERED_IP_ERROR | 등록되지 않은 IP |
| 33 | UNSIGNED_CALL_ERROR | 서명되지 않은 호출 |
| 99 | UNKNOWN_ERROR | 기타에러 |

---

## 구현 상태

### ✅ 구현 완료 (8개)
1. `getUnifyUsageCltr` - 통합용도물건목록
2. `getUnifyNewCltrList` - 신규물건목록
3. `getUnifyDeadlineCltrList` - 마감임박물건목록
4. `getUnifyPrivateContractCltrList` - 수의계약물건목록
5. `getUnifyDegression50PerCltrList` - 50%인하물건목록
6. `getUnifyClickTop20CltrList` - 조회상위20물건목록
7. `getUnifyUsageCltrBasicInfoDetail` - 물건기본정보상세
8. `getUnifyUsageCltrBidDateInfoDetail` - 입찰일정정보

**추가 구현 (공고 조회)**
- `getKamcoPlnmPbctList` - 공고목록조회
- `getKamcoPlnmPbctBasicInfoDetail` - 공고기본정보
- `getKamcoPbctSchedule` - 일정조회 ⭐
- `getKamcoPlnmPbctBidDateInfoDetail` - 공고일정상세
- `getKamcoPlnmPbctFileInfoDetail` - 첨부파일정보

### ❌ 미구현 (7개)
1. `getUnifyInterestTop20CltrList` - 관심상위20물건목록
2. `getUnifyUsageCltrEstimationInfoDetail` - 감정평가정보
3. `getUnifyUsageCltrRentalInfoDetail` - 임대차정보
4. `getUnifyUsageCltrRegisteredInfoDetail` - 등기사항정보
5. `getUnifyUsageCltrBidHistoryInfoDetail` - 입찰이력정보
6. `getUnifyUsageCltrStockholderInfoDetail` - 주주정보
7. `getUnifyUsageCltrCorporatebodyInfoDetail` - 법인재무정보

---

## 사용 예제

### 1. 기본 API 호출 구조

```python
import requests
import xmltodict
from urllib.parse import unquote

class KamcoAPI:
    def __init__(self, api_key: str):
        self.base_url = "http://openapi.onbid.co.kr/openapi/services"
        self.api_key = self._normalize_service_key(api_key)
    
    def _normalize_service_key(self, key: str) -> str:
        """Service key 중복 디코딩 방지"""
        decoded_once = unquote(key)
        decoded_twice = unquote(decoded_once)
        return decoded_twice if decoded_twice != decoded_once else decoded_once
    
    def _make_request(self, service_path: str, operation: str, params: dict):
        """공통 요청 메서드"""
        url = f"{self.base_url}/{service_path}/{operation}"
        params['serviceKey'] = self.api_key
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # XML → Dict 변환
        data = xmltodict.parse(response.text)
        
        # 결과 코드 확인
        result_code = data['response']['header']['resultCode']
        if result_code != '00':
            raise Exception(f"API Error: {data['response']['header']['resultMsg']}")
        
        return data['response']['body']
```

### 2. 최신 공고 조회 (권장 방법)

```python
from datetime import datetime, timedelta

def fetch_latest_announces(api: KamcoAPI, days: int = 7):
    """최근 N일 공고 조회 (일정 기준)"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    params = {
        'numOfRows': 100,
        'pageNo': 1,
        'SEARCH_START_DATE': start_date.strftime('%Y%m%d'),
        'SEARCH_END_DATE': end_date.strftime('%Y%m%d')
    }
    
    body = api._make_request(
        'KamcoPblsalThingInquireSvc',
        'getKamcoPbctSchedule',
        params
    )
    
    # items 추출
    items = body.get('items', {})
    if not items:
        return []
    
    schedule_list = items.get('item', [])
    if not isinstance(schedule_list, list):
        schedule_list = [schedule_list]
    
    return schedule_list
```

### 3. 물건 상세정보 조회

```python
def fetch_announce_details(api: KamcoAPI, plnm_no: str, pbct_no: str):
    """공고 기본정보 + 첨부파일"""
    # 1. 기본정보
    basic_params = {
        'PLNM_NO': plnm_no,
        'PBCT_NO': pbct_no
    }
    
    basic_body = api._make_request(
        'KamcoPblsalThingInquireSvc',
        'getKamcoPlnmPbctBasicInfoDetail',
        basic_params
    )
    
    # ⚠️ 주의: body.item (NOT body.items.item)
    basic_info = basic_body.get('item', {})
    
    # 2. 첨부파일
    file_params = {
        'PLNM_NO': plnm_no,
        'PBCT_NO': pbct_no,
        'numOfRows': 100,
        'pageNo': 1
    }
    
    file_body = api._make_request(
        'KamcoPblsalThingInquireSvc',
        'getKamcoPlnmPbctFileInfoDetail',
        file_params
    )
    
    # 중복 제거
    files = file_body.get('items', {}).get('item', [])
    if not isinstance(files, list):
        files = [files]
    
    unique_files = {}
    for file in files:
        file_id = file.get("ATCH_FILE_PTCS_NO")
        if file_id and file_id not in unique_files:
            unique_files[file_id] = file
    
    return {
        'basic_info': basic_info,
        'files': list(unique_files.values())
    }
```

### 4. MongoDB 저장

```python
from pymongo import MongoClient

def save_to_mongodb(client: MongoClient, data: dict):
    """MongoDB 저장 (Upsert)"""
    db = client['kamco']
    collection = db['collected_items']
    
    # 고유 키: PLNM_NO + PBCT_NO
    query = {
        'basic_info.PLNM_NO': data['basic_info']['PLNM_NO'],
        'basic_info.PBCT_NO': data['basic_info']['PBCT_NO']
    }
    
    # Upsert (없으면 삽입, 있으면 업데이트)
    result = collection.replace_one(
        query,
        data,
        upsert=True
    )
    
    return result.upserted_id or result.matched_count
```

---

## 데이터 품질 이슈 및 해결방안

### 문제 1: getKamcoPlnmPbctList 정렬 문제

**증상**
- 2024년 공고와 2018년 공고가 섞여 반환됨
- 최신 공고만 조회하려 해도 과거 데이터 혼재

**원인**
- API가 등록일/입찰일 기준 정렬을 제공하지 않음

**해결방안** ⭐
```python
# ❌ 사용 금지
# api.fetch_announce_list()

# ✅ 권장: 일정 기준 조회
schedules = api.fetch_schedule_list(
    start_date='20250101',
    end_date='20251231'
)

# 공고번호 중복 제거
unique_announces = {}
for schedule in schedules:
    plnm_no = schedule['PLNM_NO']
    if plnm_no not in unique_announces:
        unique_announces[plnm_no] = schedule

# 상세정보 조회
for announce in unique_announces.values():
    details = api.fetch_announce_details(
        announce['PLNM_NO'],
        announce['PBCT_NO']
    )
```

### 문제 2: 첨부파일 중복

**증상**
- 같은 파일이 여러 물건에 중복 첨부됨
- 파일 목록에 동일 파일이 여러 번 표시됨

**해결방안**
```python
def deduplicate_files(files: list) -> list:
    """ATCH_FILE_PTCS_NO 기준 중복 제거"""
    unique = {}
    for file in files:
        file_id = file.get("ATCH_FILE_PTCS_NO")
        if file_id and file_id not in unique:
            unique[file_id] = file
    return list(unique.values())
```

### 문제 3: 응답 구조 불일치

**증상**
- `getKamcoPlnmPbctBasicInfoDetail`은 `body.item` 구조
- 다른 API들은 `body.items.item` 구조

**해결방안**
```python
def safe_extract_items(body: dict, list_api: bool = True) -> list:
    """안전한 items 추출"""
    if list_api:
        # 목록 API: body.items.item
        items = body.get('items', {})
        if not items:
            return []
        item_list = items.get('item', [])
    else:
        # 상세 API: body.item
        item = body.get('item', {})
        if not item:
            return []
        item_list = [item] if not isinstance(item, list) else item
    
    # 단일 항목을 리스트로 변환
    if not isinstance(item_list, list):
        item_list = [item_list]
    
    return item_list
```

---

## 파일 매핑

### API 테스트 파일
- `tests/test_api_cli.py` - 통합용도물건 테스트
- `tests/test_api_simple.py` - 신규/마감/수의계약 테스트
- `tests/test_api_rag.py` - 50%인하/조회상위20 테스트
- `tests/test_latest_announces.py` - 일정 기준 최신 공고 조회
- `tests/test_collect_latest.py` - CLI 최신 공고 수집 스크립트

### 서비스 구현
- `services/kamco_collector_service.py` - 핵심 수집 서비스 (408 lines)

### 웹 애플리케이션
- `web/app.py` - Flask 웹서버 (257+ lines)
- `web/templates/` - 웹 UI 템플릿
  - `index.html` - 대시보드
  - `collect.html` - 수집 관리
  - `list.html` - 공고 목록
  - `detail.html` - 상세보기

---

## 추가 개발 제안

### 우선순위 높음
1. ✅ **일정 기준 최신 공고 수집** (완료)
2. ✅ **첨부파일 중복 제거** (완료)
3. ✅ **웹 UI 듀얼 데이터 구조 지원** (완료)
4. ⏳ **입찰이력정보 API 구현** - 낙찰 정보 추적
5. ⏳ **감정평가정보 API 구현** - 가격 분석

### 우선순위 중간
1. ⏳ **등기사항정보 API** - 법적 권리 분석
2. ⏳ **임대차정보 API** - 수익성 분석
3. ⏳ **관심상위20물건 API** - 인기 물건 트래킹

### 우선순위 낮음
1. ⏳ **주주정보 API** - 주식 물건용
2. ⏳ **법인재무정보 API** - 기업 분석용

---

## 라이선스 및 주의사항

### 데이터 이용 약관
- 공공데이터포털 이용약관 준수
- 상업적 이용 시 별도 협의 필요
- 데이터 재배포 금지

### API 사용 제한
- 일일 요청 횟수 제한 가능
- TPS 제한: 40 requests/sec
- 과도한 요청 시 차단 가능

### 개인정보 보호
- API 응답에 개인정보 포함 가능
- 개인정보 처리방침 준수 필요
- 민감정보 마스킹 권장

---

## 문의 및 지원

### KAMCO 공공데이터 지원
- **전화**: 051-794-4588
- **웹사이트**: https://www.onbid.co.kr
- **공공데이터포털**: https://www.data.go.kr

### 개발자 문의
- **GitHub Issues**: (프로젝트 저장소)
- **Email**: (담당자 이메일)

---

## 버전 히스토리

### v1.2 (2025-01-XX)
- ✅ 공식 OpenAPI 가이드 기반 문서 작성
- ✅ 15개 API 전체 명세 정리
- ✅ 데이터 품질 이슈 해결방안 문서화
- ✅ 최신 공고 조회 전략 수립

### v1.1 (2025-01-XX)
- ✅ 일정 기준 최신 공고 수집 구현
- ✅ 첨부파일 중복 제거 로직 추가
- ✅ 웹 UI 듀얼 데이터 구조 지원

### v1.0 (Initial)
- ✅ 6개 API 테스트 스크립트 작성
- ✅ MongoDB 연동
- ✅ Flask 웹 애플리케이션 구축
- ✅ 기본 수집 서비스 구현

---

**문서 작성일**: 2025-01-XX  
**마지막 업데이트**: 2025-01-XX  
**작성자**: GitHub Copilot  
**기반 문서**: 캠코 OpenAPI활용가이드 v1.2 (127 pages)
