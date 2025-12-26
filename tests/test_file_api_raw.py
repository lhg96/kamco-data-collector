"""첨부파일 API 원본 응답 확인"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import requests
import xmltodict
import json
from urllib.parse import unquote

load_dotenv()

def normalize_service_key(encoded_key: str) -> str:
    """서비스 키 정규화"""
    key = encoded_key
    for _ in range(2):
        try:
            decoded = unquote(key)
            if decoded == key:
                break
            key = decoded
        except Exception:
            break
    return key

service_key = normalize_service_key(os.getenv("KAMCO_SERVICE_KEY_ENCODED"))
base_url = "http://openapi.onbid.co.kr/openapi/services"
service_path = "KamcoPblsalThingInquireSvc"

url = f"{base_url}/{service_path}/getKamcoPlnmPbctFileInfoDetail"
params = {
    "serviceKey": service_key,
    "numOfRows": 10,
    "pageNo": 1,
    "PLNM_NO": "464351",
    "PBCT_NO": "9314139",
}

print("=" * 80)
print("첨부파일 API 원본 응답 확인")
print("=" * 80)
print(f"URL: {url}")
print(f"PLNM_NO: {params['PLNM_NO']}, PBCT_NO: {params['PBCT_NO']}")
print()

try:
    res = requests.get(url, params=params, timeout=30)
    res.raise_for_status()
    
    print("=" * 80)
    print("XML 응답:")
    print("=" * 80)
    print(res.text)
    print()
    
    print("=" * 80)
    print("파싱 결과:")
    print("=" * 80)
    payload = xmltodict.parse(res.text)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # items 확인
    body = (payload.get("response") or {}).get("body") or {}
    items = body.get("items")
    if items:
        file_info = items.get("fileItem")
        print()
        print("=" * 80)
        print("fileItem 타입:", type(file_info))
        print("fileItem 개수:", len(file_info) if isinstance(file_info, list) else 1)
        print("=" * 80)
        
except Exception as e:
    print(f"오류 발생: {e}")
