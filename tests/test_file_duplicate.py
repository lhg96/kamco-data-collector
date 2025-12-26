"""첨부파일 중복 테스트"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.kamco_collector_service import KamcoCollectorService
from dotenv import load_dotenv
import json

load_dotenv()

service = KamcoCollectorService()

# 특정 공고의 첨부파일 조회
print("=" * 80)
print("첨부파일 정보 조회 테스트")
print("=" * 80)

# 사용자가 언급한 파일이 있을 가능성이 높은 공고번호
test_cases = [
    ('464351', '9314139'),  # 기존 테스트 케이스
    ('407681', '9248754'),  # 0002 재산구분에서 수집된 케이스
]

for plnm_no, pbct_no in test_cases:
    print(f"\n→ PLNM_NO: {plnm_no}, PBCT_NO: {pbct_no}")
    files = service.fetch_file_info(plnm_no, pbct_no)
    
    if files:
        print(f"  총 파일 개수: {len(files)}개")
        
        # 파일 상세 정보 출력
        for i, f in enumerate(files, 1):
            print(f"  [{i}] {f.get('ATCH_FILE_NM')}")
            print(f"      파일번호: {f.get('ATCH_FILE_PTCS_NO')}")
            print(f"      경로: {f.get('FILE_PTH_CNTN')}")
            print()
        
        # 중복 확인
        file_ids = [f.get('ATCH_FILE_PTCS_NO') for f in files]
        unique_file_ids = set(file_ids)
        if len(file_ids) != len(unique_file_ids):
            print(f"  ⚠️  중복 발견! 전체: {len(file_ids)}개, 고유: {len(unique_file_ids)}개")
        else:
            print(f"  ✅ 중복 없음")
    else:
        print(f"  첨부파일 없음")

print("\n" + "=" * 80)
