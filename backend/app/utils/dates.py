from datetime import date


def nights_between(check_in: date, check_out: date) -> int:
    """Return the number of booked nights after caller-side validation."""
    return (check_out - check_in).days
