"""
Optional integration check for the running FastAPI /ask endpoint.
Skipped unless RUN_INTEGRATION=1 is set in the environment.
"""

import os

import pytest
import requests


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run live API check")
def test_live_ask_endpoint():
    api_url = os.getenv("KAMCO_API_URL", "http://localhost:8000/ask")
    question = os.getenv("KAMCO_TEST_QUESTION", "캠코 공매 일정은 어떻게 확인하나요?")

    res = requests.get(api_url, params={"q": question}, timeout=60)
    res.raise_for_status()
    data = res.json()

    assert "answer" in data
    assert "matches" in data
