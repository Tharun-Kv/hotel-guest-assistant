import re


def normalize_message(value: str) -> str:
    """Collapse whitespace before intent matching without changing meaning."""
    return re.sub(r"\s+", " ", value).strip()
