from app.ai.intent import detect_intent


def test_detect_faq_intent():
    intent = detect_intent("What time is check-in?")
    assert intent == "faq"


def test_detect_amenity_intent():
    intent = detect_intent("Does the hotel have a swimming pool?")
    assert intent == "amenity"


def test_detect_room_information_intent():
    intent = detect_intent("Which room is good for three people?")
    assert intent == "room_information"


def test_detect_availability_intent():
    intent = detect_intent("Do you have rooms from October 10 to October 12?")
    assert intent == "availability"


def test_detect_unknown_intent():
    intent = detect_intent("Do you have a helicopter?")
    assert intent == "unknown"


def test_detect_identity_questions_without_an_ai_key():
    assert detect_intent("who are u") == "identity"
    assert detect_intent("which asisitance are u") == "identity"
