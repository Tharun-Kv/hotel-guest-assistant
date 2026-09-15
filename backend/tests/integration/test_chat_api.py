from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_chat_api_checkin_question():
    response = client.post("/api/chat", json={"message": "What time is check-in?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "check-in" in data["message"].lower()


def test_chat_api_greeting_returns_a_welcome_message():
    response = client.post("/api/chat", json={"message": "hi"})
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "answer"
    assert "hello" in data["message"].lower()


def test_chat_api_identity_questions_return_capabilities():
    for message in ("who are u", "which asisitance are u"):
        response = client.post("/api/chat", json={"message": message})
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "answer"
        assert "virtual assistant" in data["message"].lower()
        assert "availability" in data["message"].lower()


def test_chat_api_does_not_expose_hotel_contact_for_personal_phone_request():
    response = client.post("/api/chat", json={"message": "What is your phone number?"})

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "answer"
    assert "personal phone number" in data["message"].lower()
    assert "+1 (206) 555-0147" not in data["message"]


def test_chat_api_room_question():
    response = client.post("/api/chat", json={"message": "Which room is good for 3 people?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "room" in data["message"].lower()


def test_chat_api_unknown_question():
    response = client.post("/api/chat", json={"message": "Do you have a helicopter?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sorry" in data["message"].lower() or "cannot" in data["message"].lower()


def test_chat_api_follow_up_question():
    payload = {"message": "Do you have rooms for 3 people?", "conversation": [{"role": "user", "content": "Hello"}]}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    first = response.json()
    follow = client.post("/api/chat", json={"message": "What about breakfast?", "conversation": [{"role": "user", "content": "Do you have rooms for 3 people?"}, {"role": "assistant", "content": first["message"]}]})
    assert follow.status_code == 200
    assert follow.json()["success"] is True


def test_chat_api_missing_availability_dates_requests_clarification():
    response = client.post("/api/chat", json={"message": "Are rooms available for 3 guests?"})
    assert response.status_code == 200
    assert response.json()["type"] == "clarification"


def test_chat_api_preserves_server_conversation_id():
    first = client.post("/api/chat", json={"message": "What time is check-in?"})
    conversation_id = first.json()["conversation_id"]
    follow_up = client.post("/api/chat", json={"message": "What about breakfast?", "conversation_id": conversation_id})
    assert follow_up.status_code == 200
    assert follow_up.json()["conversation_id"] == conversation_id
    assert "breakfast" in follow_up.json()["message"].lower()
