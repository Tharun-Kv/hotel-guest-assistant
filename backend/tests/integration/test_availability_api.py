from datetime import date, timedelta

from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_availability_api_valid_request():
    check_in = date.today() + timedelta(days=20)
    check_out = check_in + timedelta(days=2)
    response = client.post(
        "/api/availability",
        json={"check_in": check_in.isoformat(), "check_out": check_out.isoformat(), "adults": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert "rooms" in data


def test_availability_api_invalid_range():
    today = date.today()
    response = client.post(
        "/api/availability",
        json={"check_in": today.isoformat(), "check_out": today.isoformat(), "adults": 2},
    )
    assert response.status_code == 422
