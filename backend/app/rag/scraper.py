"""Safe, lightweight HTML ingestion for hotel documentation pages."""

from html.parser import HTMLParser
from ipaddress import ip_address
from urllib.parse import urlparse

import httpx


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self._in_title = False
        self._text: list[str] = []
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg", "nav", "footer"}:
            self._ignored_depth += 1
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg", "nav", "footer"} and self._ignored_depth:
            self._ignored_depth -= 1
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        value = " ".join(data.split())
        if not value:
            return
        self._text.append(value)
        if self._in_title:
            self.title_parts.append(value)

    @property
    def text(self) -> str:
        return " ".join(self._text)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()


def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP or HTTPS URLs can be ingested.")
    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "127.0.0.1", "::1"} or hostname.endswith(".local"):
        raise ValueError("Local network URLs cannot be ingested.")
    try:
        address = ip_address(hostname)
        if address.is_private or address.is_loopback or address.is_reserved or address.is_link_local:
            raise ValueError("Private network URLs cannot be ingested.")
    except ValueError as exc:
        if str(exc).endswith("cannot be ingested."):
            raise


def scrape_url(url: str, max_bytes: int = 2_000_000) -> tuple[str, str]:
    _validate_public_url(url)
    try:
        response = httpx.get(url, follow_redirects=True, timeout=15)
        _validate_public_url(str(response.url))
        response.raise_for_status()
    except ValueError:
        raise
    except httpx.HTTPError as exc:
        raise ValueError("The source URL could not be fetched.") from exc
    if len(response.content) > max_bytes:
        raise ValueError("The source page is larger than the 2 MB ingestion limit.")
    parser = _VisibleTextParser()
    parser.feed(response.text)
    return parser.title or url, parser.text
