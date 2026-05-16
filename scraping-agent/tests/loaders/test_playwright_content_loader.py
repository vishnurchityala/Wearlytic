import pytest

from scraperkit.exceptions import BadURLException, TimeoutException
from scraperkit.loaders.playwright_content_loader import (
    PlaywrightContentLoader,
    PlaywrightError,
)


LIVE_HTML_URL = "https://example.com/"
SLOW_RESPONSE_URL = "https://httpbin.org/delay/5"


def build_loader(**overrides):
    overrides.setdefault("headless", True)
    try:
        return PlaywrightContentLoader(**overrides)
    except PlaywrightError as exc:
        pytest.skip(f"Playwright is not available for live loader tests: {exc}")


@pytest.mark.integration
def test_playwright_loader_returns_page_content_from_real_website():
    loader = build_loader(timeout=10000)

    try:
        page_content = loader.load_content(LIVE_HTML_URL)
    finally:
        loader.close()

    assert "<html" in page_content.lower()
    assert "example domain" in page_content.lower()


@pytest.mark.integration
def test_playwright_loader_wraps_timeouts_against_real_website():
    loader = build_loader(timeout=100)

    try:
        with pytest.raises(TimeoutException):
            loader.load_content(SLOW_RESPONSE_URL)
    finally:
        loader.close()


@pytest.mark.integration
def test_playwright_loader_wraps_bad_urls_with_real_browser():
    loader = build_loader(timeout=10000)

    try:
        with pytest.raises(BadURLException):
            loader.load_content("notaurl")
    finally:
        loader.close()


@pytest.mark.integration
def test_playwright_loader_closes_real_page_and_browser():
    loader = build_loader(timeout=10000)
    page = loader.page
    browser = loader.browser

    loader.close()

    assert page.is_closed() is True
    assert browser.is_connected() is False
