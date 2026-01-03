"""
Step 3: Embed Data
Test the KAMCO Data Embedding (Qdrant Upsert).
"""
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.embed import embed, setup_collection

logging.basicConfig(level=logging.INFO)

def run_step3():
    print(">>> [Step 3] Testing Embedding...")
    
    # Setup Collection (Safe to run multiple times, checks existence)
    try:
        print(">>> Checking/Creating Qdrant Collection...")
        setup_collection()
        print("✅ Collection ready.")
    except Exception as e:
        print(f"❌ Collection setup failed: {e}")
        # Proceeding might fail, but let's try embed
    
    # Run Embedding
    try:
        print(">>> Running full embedding...")
        count = embed()
        print(f"✅ Embedded {count} items.")
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_step3()
