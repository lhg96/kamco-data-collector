# KAMCO 첨부파일 중복 문제 해결

## 문제 상황
KAMCO OpenAPI에서 첨부파일 정보를 조회할 때, **동일한 파일이 중복으로 반환**되는 API 자체의 데이터 품질 문제가 발견되었습니다.

### 예시
```xml
<fileItem>
    <ATCH_FILE_PTCS_NO>8124406</ATCH_FILE_PTCS_NO>
    <ATCH_FILE_NM>2017년도 제10회 수탁재산 공고문.hwp</ATCH_FILE_NM>
    <FILE_PTH_CNTN>/jmsdata/shared/mp/announce/2017/1012</FILE_PTH_CNTN>
</fileItem>
<fileItem>
    <ATCH_FILE_PTCS_NO>8124406</ATCH_FILE_PTCS_NO>
    <ATCH_FILE_NM>2017년도 제10회 수탁재산 공고문.hwp</ATCH_FILE_NM>
    <FILE_PTH_CNTN>/jmsdata/shared/mp/announce/2017/1012</FILE_PTH_CNTN>
</fileItem>
```

같은 파일번호(ATCH_FILE_PTCS_NO)로 동일한 파일이 2~5번 중복되어 나타납니다.

## 해결 방법

### 1. 데이터 수집 시점 중복 제거
**파일:** `services/kamco_collector_service.py`

`fetch_file_info()` 메서드에서 파일번호(`ATCH_FILE_PTCS_NO`) 기준으로 중복을 제거합니다.

```python
# 중복 제거 (파일번호 기준)
seen = set()
unique_files = []
for file in file_list:
    file_id = file.get('ATCH_FILE_PTCS_NO')
    if file_id and file_id not in seen:
        seen.add(file_id)
        unique_files.append(file)

return unique_files
```

### 2. 기존 MongoDB 데이터 정리
**파일:** `scripts/clean_duplicate_files.py`

이미 저장된 중복 데이터를 일괄 정리하는 스크립트를 실행합니다.

```bash
python scripts/clean_duplicate_files.py
```

**결과:**
- 업데이트된 문서: 17개
- 제거된 중복 파일: 58개

### 3. 웹 화면 표시 시 추가 보호
**파일:** `web/app.py`

`detail_page()` 라우트에서 표시 전 한 번 더 중복을 확인하고 제거합니다.

```python
# 첨부파일 중복 제거 (추가 보호)
if item.get('file_info'):
    seen = set()
    unique_files = []
    for file in item['file_info']:
        file_id = file.get('ATCH_FILE_PTCS_NO')
        if file_id and file_id not in seen:
            seen.add(file_id)
            unique_files.append(file)
    item['file_info'] = unique_files
```

## 테스트

### 중복 확인 테스트
```bash
python tests/test_file_duplicate.py
```

**결과:**
```
→ PLNM_NO: 464351, PBCT_NO: 9314139
  총 파일 개수: 1개
  [1] 2017년도 제10회 수탁재산 공고문.hwp
      파일번호: 8124406
      경로: /jmsdata/shared/mp/announce/2017/1012

  ✅ 중복 없음
```

### API 원본 응답 확인
```bash
python tests/test_file_api_raw.py
```

API가 중복으로 반환하더라도 우리 시스템에서는 자동으로 제거됩니다.

## 적용된 파일

1. ✅ `services/kamco_collector_service.py` - 수집 시점 중복 제거
2. ✅ `scripts/clean_duplicate_files.py` - 기존 데이터 정리 스크립트
3. ✅ `web/app.py` - 웹 표시 시 추가 보호
4. ✅ `tests/test_file_duplicate.py` - 중복 확인 테스트
5. ✅ `tests/test_file_api_raw.py` - API 원본 응답 확인

## 결론

KAMCO OpenAPI의 데이터 품질 문제를 3단계 방어로 해결했습니다:
1. **수집 시점** - API 응답에서 중복 제거
2. **저장 데이터** - 기존 MongoDB 데이터 정리
3. **표시 시점** - 웹 화면 표시 전 최종 확인

이제 첨부파일이 중복으로 표시되지 않습니다.
