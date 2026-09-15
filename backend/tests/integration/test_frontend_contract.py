"""Frontend-facing contract smoke tests for the two interactive flows."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_to_availability_payload_contract():
    check_in = date.today() + timedelta(days=40)
    check_out = check_in + timedelta(days=2)
    response = client.post(
        "/api/chat",
        json={"message": f"Are rooms available from {check_in} to {check_out} for 3 guests?"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["type"] == "availability"
    assert data["availability"]["check_in"] == check_in.isoformat()
    assert isinstance(data["availability"]["rooms"], list)
