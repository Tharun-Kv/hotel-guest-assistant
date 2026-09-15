from app.services.hotel_service import HotelService


service = HotelService()


def test_hotel_has_expected_contact_information():
    hotel = service.get_hotel()
    assert hotel["name"] == "Harbor View Hotel"
    assert hotel["address"]


def test_faq_lookup_returns_expected_value():
    faq = service.get_faq("check-in")
    assert "check-in" in faq["question"].lower()


def test_room_lookup_by_id():
    room = service.get_room_by_id("STD001")
    assert room["room_id"] == "STD001"


def test_room_recommendation_for_three_people():
    rooms = service.find_suitable_rooms(3)
    assert any(room["capacity"] >= 3 for room in rooms)


def test_room_recommendation_returns_no_room_above_published_capacity():
    assert service.find_suitable_rooms(6) == []
