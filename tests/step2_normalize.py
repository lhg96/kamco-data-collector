"""
Step 2: Normalize Data
Test the KAMCO Data Normalization logic.
"""
import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from normalize.kamco_normalizer import normalize, _build_text_from_collected

logging.basicConfig(level=logging.INFO)

def run_step2():
    print(">>> [Step 2] Testing Normalization...")
    
    # Unit Test Normalization Logic
    sample_item = {
        "basic_info": {
            "pblancNm": "2025년도 제12회 수탁재산 공매공고",
            "lctnAddr": "서울시 강남구",
            "lwsbidPrc": "100,000,000",
            "pbancBgngYmd": "20250101",
            "pbancEndYmd": "20250110",
            "PLNM_NO": "20251234",
            "PBCT_NO": "12345"
        }
    }
    
    try:
        text = _build_text_from_collected(sample_item)
        print(">>> Sample Normalized Text:")
        print(text)
        
        if "2025년도 제12회" in text and "강남구" in text:
            print("✅ Normalization logic passed.")
        else:
            print("❌ Normalization logic check failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Normalization Unit Test Failed: {e}")
        sys.exit(1)

    # Run Full Normalization on DB
    try:
        print(">>> Running full DB normalization...")
        count = normalize()
        print(f"✅ Normalized {count} items in total.")
    except Exception as e:
        print(f"❌ Full Normalization Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_step2()
