import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from main import app


def test_health_returns_200():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200