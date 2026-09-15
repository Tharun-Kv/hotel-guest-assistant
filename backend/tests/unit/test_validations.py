from datetime import date, timedelta

from app.utils.validation import validate_date_range, validate_guest_count


def test_validate_date_range_accepts_valid_range():
    check_in = date.today() + timedelta(days=5)
    check_out = check_in + timedelta(days=2)
    assert validate_date_range(check_in, check_out) is None


def test_validate_date_range_rejects_same_day_checkout():
    check_in = date.today() + timedelta(days=5)
    try:
        validate_date_range(check_in, check_in)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_validate_guest_count_rejects_invalid_count():
    try:
        validate_guest_count(0)
        assert False, "Expected ValueError"
    except ValueError:
        pass
