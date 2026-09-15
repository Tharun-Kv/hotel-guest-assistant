from datetime import date

from app.core.config import settings


def validate_date_range(check_in: date, check_out: date) -> None:
    if check_in is None or check_out is None:
        raise ValueError("Check-in and check-out dates are required.")
    if check_in < date.today():
        raise ValueError("Check-in date cannot be in the past.")
    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date.")


def validate_guest_count(adults: int) -> None:
    if adults is None or not 1 <= adults <= settings.MAX_GUESTS:
        raise ValueError(f"The number of guests must be between 1 and {settings.MAX_GUESTS}.")
