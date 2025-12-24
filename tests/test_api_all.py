"""
캠코 6가지 API 전체 테스트 실행 스크립트

실행:
  python tests/test_api_all.py

환경변수 (.env):
  KAMCO_SERVICE_KEY_ENCODED
"""

import os
import sys
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def run_test_script(script_path: Path, test_name: str) -> bool:
    """개별 테스트 스크립트를 실행합니다."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}[{test_name}]{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}")
    
    try:
        # 모듈 동적 로드
        spec = importlib.util.spec_from_file_location("test_module", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # main 함수 실행
        if hasattr(module, 'main'):
            result = module.main()
            if result == 0:
                print(f"{GREEN}{BOLD}✓ {test_name} 성공{RESET}\n")
                return True
            else:
                print(f"{RED}{BOLD}✗ {test_name} 실패 (exit code: {result}){RESET}\n")
                return False
        else:
            print(f"{RED}✗ main() 함수를 찾을 수 없습니다.{RESET}\n")
            return False
            
    except Exception as e:
        print(f"{RED}✗ 테스트 실행 중 오류: {e}{RESET}\n")
        return False


def main() -> int:
    # API 키 확인
    if not os.getenv("KAMCO_SERVICE_KEY_ENCODED"):
        print(f"{RED}❌ KAMCO_SERVICE_KEY_ENCODED is not set in .env{RESET}")
        return 1
    
    print(f"{BOLD}{GREEN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}캠코 6가지 API 전체 테스트 시작{RESET}")
    print(f"{BOLD}{GREEN}{'='*80}{RESET}\n")
    
    # 테스트 목록
    tests = [
        ("test_api_01_cltr_list.py", "1. 캠코공매물건목록조회"),
        ("test_api_02_announce_list.py", "2. 캠코공매공고목록조회"),
        ("test_api_03_announce_basic.py", "3. 캠코공매공고 기본정보 상세조회"),
        ("test_api_04_schedule.py", "4. 캠코공매일정조회"),
        ("test_api_05_announce_schedule.py", "5. 캠코공매공고 공매일정 상세조회"),
        ("test_api_06_announce_file.py", "6. 캠코공매공고 첨부파일 상세조회"),
    ]
    
    # 현재 스크립트의 디렉토리
    current_dir = Path(__file__).parent
    
    results = []
    
    for script_name, test_name in tests:
        script_path = current_dir / script_name
        
        if not script_path.exists():
            print(f"{RED}✗ {script_path} 파일을 찾을 수 없습니다.{RESET}")
            results.append((test_name, False))
            continue
        
        success = run_test_script(script_path, test_name)
        results.append((test_name, success))
    
    # 결과 요약
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}테스트 결과 요약{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = f"{GREEN}✓ 성공{RESET}" if success else f"{RED}✗ 실패{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BOLD}총 {success_count}/{total_count} 테스트 성공{RESET}")
    
    if success_count == total_count:
        print(f"{GREEN}{BOLD}\n🎉 모든 테스트가 성공했습니다!{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}{BOLD}\n⚠️  일부 테스트가 실패했습니다.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
