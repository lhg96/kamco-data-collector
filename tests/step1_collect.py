"""
Step 1: Collect Data
Test the KAMCO Data Collection Service.
"""
import sys
import os
import logging
from pprint import pprint

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.kamco_collector_service import KamcoCollectorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("step1_collect")

def run_step1():
    print(">>> [Step 1] Testing Data Collection...")
    
    # Initialize Service
    try:
        service = KamcoCollectorService()
        print("✅ Service initialized.")
    except Exception as e:
        print(f"❌ Service init failed: {e}")
        sys.exit(1)

    # Test connection
    if not service.connect_mongodb():
        print("❌ MongoDB connection failed.")
        sys.exit(1)
    print("✅ MongoDB connected.")

    # Run collection (Small batch for testing)
    # Fetch just 1 page, 5 rows to ensure it works
    try:
        print(">>> Fetching 5 items from KAMCO API...")
        stats = service.run(page_no=1, num_of_rows=5, save_to_db=True)
        pprint(stats)
        
        saved = stats.get("saved_items", 0)
        if saved > 0:
            print(f"✅ Successfully collected {saved} items.")
        else:
            print("⚠️ No items saved. (Check API key or DB state)")
            
    except Exception as e:
        print(f"❌ Collection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_step1()
