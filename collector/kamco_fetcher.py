"""Fetch KAMCO(OpenAPI) data and store raw responses into MongoDB."""

from datetime import datetime
import logging
import os

import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

API_KEY = os.getenv("KAMCO_API_KEY")
BASE_URL = os.getenv(
    "KAMCO_BASE_URL",
    "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getApplyhomeInfoDetail",
)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
PAGE_SIZE = int(os.getenv("KAMCO_PAGE_SIZE", "100"))

mongo = MongoClient(MONGO_URI)
db = mongo.kamco
raw_col = db.raw_items

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)
session = requests.Session()


def fetch_kamco(page: int = 1, per_page: int = PAGE_SIZE) -> dict:
    """Call the public KAMCO API and return the parsed JSON response."""
    if not API_KEY:
        raise RuntimeError("KAMCO_API_KEY is not set.")

    params = {
        "serviceKey": API_KEY,
        "page": page,
        "perPage": per_page,
        "returnType": "JSON",
    }
    r = session.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def run() -> None:
    page = 1
    while True:
        data = fetch_kamco(page=page, per_page=PAGE_SIZE)
        items = data.get("data") or []
        if not items:
            log.info("No more items at page %s; stopping.", page)
            break

        for item in items:
            doc_id = item.get("pblancNo") or f"{page}-{item.get('cltrNo', '')}"
            raw_col.update_one(
                {"_id": doc_id},
                {"$set": {"raw": item, "fetched_at": datetime.utcnow()}},
                upsert=True,
            )

        log.info("Stored %s items from page %s", len(items), page)
        page += 1


if __name__ == "__main__":
    run()
