# KAMCO 공매 데이터 수집 관리 웹 시스템

Flask 기반의 KAMCO 공매 데이터 수집 관리 웹 애플리케이션입니다.

## 기능

### 1. 대시보드 (`/`)
- 전체 수집 데이터 통계
- 오늘 수집한 데이터 통계
- 최근 수집 데이터 미리보기
- 빠른 액션 버튼

### 2. 데이터 수집 (`/collect`)
- 수집 설정 (페이지 번호, 조회 건수, 재산구분코드)
- 실시간 수집 진행 상태 표시
- 수집 결과 통계 표시
- 수집된 데이터 자동 MongoDB 저장

### 3. 수집 목록 (`/list`)
- 페이지네이션 지원 (기본 20개씩)
- 검색 기능 (공고번호, 공매번호, 공고명)
- 공매 일정 및 첨부파일 개수 표시
- 데이터 삭제 기능

### 4. 상세보기 (`/detail/<item_id>`)
- 공고 기본 정보
- 공매 일정 상세
- 첨부 파일 목록
- 메타 정보 (수집 시간 등)

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)

```env
# KAMCO API 키 (필수)
KAMCO_SERVICE_KEY_ENCODED=your_encoded_api_key_here

# MongoDB 설정 (선택사항)
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=kamco
MONGO_COLLECTION_NAME=collected_items

# Flask 설정 (선택사항)
FLASK_PORT=5000
FLASK_SECRET_KEY=your_secret_key_here
```

### 3. 서버 실행

```bash
python web/app.py
```

또는

```bash
cd web
python app.py
```

### 4. 브라우저에서 접속

```
http://localhost:5000
```

## 프로젝트 구조

```
web/
├── app.py                    # Flask 메인 애플리케이션
├── templates/                # HTML 템플릿
│   ├── base.html            # 기본 레이아웃
│   ├── index.html           # 대시보드
│   ├── collect.html         # 데이터 수집 페이지
│   ├── list.html            # 수집 목록 페이지
│   ├── detail.html          # 상세보기 페이지
│   └── error.html           # 오류 페이지
├── static/                   # 정적 파일 (CSS, JS, 이미지)
└── README.md                # 이 파일
```

## API 엔드포인트

### POST /api/collect
데이터 수집 실행

**요청 파라미터:**
- `page_no`: 페이지 번호 (기본값: 1)
- `num_of_rows`: 조회 건수 (기본값: 10, 최대: 100)
- `prpt_dvsn_cd`: 재산구분코드 (기본값: 0001)

**응답:**
```json
{
  "success": true,
  "stats": {
    "total_announces": 10,
    "processed_announces": 10,
    "failed_announces": 0,
    "saved_items": 10
  },
  "message": "10개 항목이 수집되었습니다."
}
```

### POST /api/delete/<item_id>
데이터 삭제

**응답:**
```json
{
  "success": true,
  "message": "삭제되었습니다."
}
```

## 재산구분코드

- `0001`: 금융권담보재산
- `0002`: 비금융권담보재산
- `0003`: 압류재산
- `0004`: 국유재산
- `0005`: 기타일반재산

## 기술 스택

- **Backend**: Flask 3.0+
- **Database**: MongoDB
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **Data Collection**: KamcoCollectorService
- **APIs**: KAMCO OpenAPI

## 주의사항

1. **MongoDB 연결**: MongoDB가 실행 중이어야 합니다.
2. **API 키**: KAMCO API 키가 `.env` 파일에 설정되어야 합니다.
3. **수집 시간**: 데이터 수집은 시간이 걸릴 수 있습니다.
4. **중복 처리**: 동일한 공고번호+공매번호는 자동으로 업데이트됩니다.

## 문제 해결

### MongoDB 연결 실패
```bash
# MongoDB 실행 확인
mongosh

# 또는 Docker로 MongoDB 실행
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### API 키 오류
- `.env` 파일에 `KAMCO_SERVICE_KEY_ENCODED` 값이 올바르게 설정되었는지 확인
- URL 인코딩된 키를 사용해야 합니다

### 포트 충돌
```bash
# 다른 포트로 실행
FLASK_PORT=8080 python web/app.py
```

## 개발 모드

디버그 모드는 기본적으로 활성화되어 있습니다. 프로덕션에서는 비활성화하세요:

```python
# web/app.py
app.run(debug=False, host='0.0.0.0', port=port)
```

## 라이선스

MIT License
