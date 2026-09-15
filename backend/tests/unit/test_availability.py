from datetime import date, timedelta

from app.services.availability_service import AvailabilityService


service = AvailabilityService()


def test_availability_returns_room_for_three_guests():
    check_in = date.today() + timedelta(days=10)
    check_out = check_in + timedelta(days=2)
    result = service.check_availability(check_in, check_out, adults=3)
    assert result["available"] is True
    assert len(result["rooms"]) >= 1


def test_availability_rejects_invalid_range():
    check_in = date.today() + timedelta(days=10)
    try:
        service.check_availability(check_in, check_in, adults=2)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_availability_rejects_invalid_guest_count():
    check_in = date.today() + timedelta(days=10)
    check_out = check_in + timedelta(days=2)
    try:
        service.check_availability(check_in, check_out, adults=0)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_interval_overlap_allows_same_day_checkout_and_checkin():
    check_in = date.today() + timedelta(days=30)
    check_out = check_in + timedelta(days=2)
    assert service.has_overlap(check_in, check_out, check_out, check_out + timedelta(days=2)) is False
    assert service.has_overlap(check_in, check_out, check_in + timedelta(days=1), check_out + timedelta(days=1)) is True
