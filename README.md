# KAMCO 데이터 수집 · RAG 파이프라인

Cloudflare 프론트/Workers를 거쳐 Mac mini에서 수집·임베딩·질의를 수행하는 구성입니다.

```
[Cloudflare Front]
        ↓
[Cloudflare Workers]
        ↓ (Tunnel)
[Mac mini]
 ├─ FastAPI (/ask)
 ├─ MongoDB (raw + metadata)
 ├─ Qdrant (vector)
 ├─ Ollama (LLM & Embedding)
 └─ Collector (KAMCO OpenAPI)
```

## 0. Mac mini 기본 환경

- MongoDB 7.0 (local)
  ```bash
  brew tap mongodb/brew
  brew install mongodb-community@7.0
  brew services start mongodb-community
  ```
- Ollama
  ```bash
  brew install ollama
  ollama pull qwen2.5:latest
  ```
- Qdrant
  ```bash
  docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -v ~/qdrant:/qdrant/storage \
    qdrant/qdrant
  ```

DB 스키마
```
kamco
 ├─ raw_items
 ├─ normalized_items
 └─ chunks (Qdrant payload에 대응)
```

## 1. Python 환경

```bash
cd kamco_gradio_collector
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

필수 환경 변수
```
KAMCO_API_KEY=발급받은 키
MONGO_URI=mongodb://localhost:27017
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=kamco
EMBED_MODEL=qwen2.5:latest
GEN_MODEL=qwen2.5:latest
```
`.env` 파일로 관리하면 자동 로드됩니다.

## 2. 파이프라인

1) **수집기** (`collector/kamco_fetcher.py`):  
   - OpenAPI(합법)만 사용  
   - Raw 응답을 그대로 MongoDB `raw_items` 에 upsert  
   ```bash
   python collector/kamco_fetcher.py
   ```

2) **정규화** (`normalize/kamco_normalizer.py`):  
   - Raw → 사람이 읽기 쉬운 텍스트로 변환  
   - 텍스트 SHA-256 해시 저장  
   ```bash
   python normalize/kamco_normalizer.py
   ```

3) **임베딩** (`rag/embed.py`):  
   - Ollama 임베딩(qwen2.5) → Qdrant 컬렉션 `kamco`  
   - `setup_collection()`가 컬렉션을 매번 재생성합니다(기존 데이터 초기화 주의)  
   ```bash
   python rag/embed.py
   ```

4) **RAG API** (`api/main.py`):  
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
   - `GET /ask?q=...` → 벡터 검색(Top-5) → 컨텍스트로 LLM 응답  
   - `GET /health` 헬스체크

## 3. Cloudflare Tunnel · Workers

```bash
cloudflared tunnel create kamco-rag
cloudflared tunnel run kamco-rag
```
- Workers에서 `/ask` 엔드포인트만 프록시로 연결.
- Tunnel 대상: Mac mini의 FastAPI `http://localhost:8000`.

## 4. 테스트

- API 연결 확인: `python test_api.py`  
  - 기본 URL: `http://localhost:8000/ask`  
  - 성공 시 응답과 매칭 개수를 출력합니다.
- 단위 테스트: `pytest`

## 5. 파일 구조

```
kamco_gradio_collector/
├── api/
│   └── main.py                # FastAPI /ask
├── collector/
│   └── kamco_fetcher.py       # KAMCO OpenAPI 수집기
├── normalize/
│   └── kamco_normalizer.py    # Raw → 정규화 텍스트
├── rag/
│   └── embed.py               # 임베딩 & Qdrant 업서트
├── test_api.py                # /ask 호출 테스트
├── requirements.txt
└── README.md
```
