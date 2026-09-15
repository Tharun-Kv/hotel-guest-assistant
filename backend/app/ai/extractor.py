import re
from dataclasses import dataclass
from datetime import date


MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
MONTH_PATTERN = "|".join(MONTHS)


@dataclass(frozen=True)
class AvailabilityEntities:
    check_in: date | None = None
    check_out: date | None = None
    adults: int | None = None


def extract_guest_count(message: str) -> int | None:
    text = message.lower()
    numeric = re.search(r"\b(\d+)\s*(?:adult(?:s)?|guest(?:s)?|people|person)\b", text)
    if numeric:
        return int(numeric.group(1))
    for word, value in NUMBER_WORDS.items():
        if re.search(rf"\b{word}\s+(?:adult(?:s)?|guest(?:s)?|people|person)\b", text):
            return value
    return None


def _human_date(month_name: str, day_text: str, year_text: str | None) -> date | None:
    try:
        month = MONTHS[month_name.lower()]
        year = int(year_text) if year_text else date.today().year
        parsed = date(year, month, int(day_text))
        if not year_text and parsed < date.today():
            parsed = date(year + 1, month, int(day_text))
        return parsed
    except ValueError:
        return None


def extract_dates(message: str) -> tuple[date | None, date | None]:
    iso_dates = [date.fromisoformat(value) for value in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", message)]
    if len(iso_dates) >= 2:
        return iso_dates[0], iso_dates[1]
    matches = re.findall(rf"\b({MONTH_PATTERN})\s+(\d{{1,2}})(?:,?\s*(\d{{4}}))?", message, flags=re.IGNORECASE)
    parsed_dates = [_human_date(month, day, year) for month, day, year in matches]
    parsed_dates = [item for item in parsed_dates if item is not None]
    if len(parsed_dates) >= 2:
        first_year_is_explicit = bool(matches[0][2])
        second_year_is_explicit = bool(matches[1][2])
        if (first_year_is_explicit or not second_year_is_explicit) and not second_year_is_explicit and parsed_dates[1] <= parsed_dates[0]:
            try:
                parsed_dates[1] = parsed_dates[1].replace(year=parsed_dates[0].year + 1)
            except ValueError:
                return None, None
        return parsed_dates[0], parsed_dates[1]
    return None, None


def extract_availability_entities(message: str) -> AvailabilityEntities:
    check_in, check_out = extract_dates(message)
    return AvailabilityEntities(check_in=check_in, check_out=check_out, adults=extract_guest_count(message))
