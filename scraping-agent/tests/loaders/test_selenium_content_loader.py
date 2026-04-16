import pytest

from scraperkit.exceptions import (
    BadURLException,
    ContentNotLoadedException,
    DriverNotInitializedException,
    TimeoutException,
)
from scraperkit.loaders.selenium_content_loader import SeleniumContentLoader


LIVE_HTML_URL = "https://example.com/"
SLOW_RESPONSE_URL = "https://httpbin.org/delay/5"


def build_loader(**overrides):
    overrides.setdefault("headless", True)
    try:
        return SeleniumContentLoader(**overrides)
    except DriverNotInitializedException as exc:
        pytest.skip(f"Selenium is not available for live loader tests: {exc}")


@pytest.mark.unit
def test_selenium_loader_wraps_unexpected_errors_without_real_driver(monkeypatch):
    class DummyDriver:
        def get(self, page_url):
            raise RuntimeError("boom")

        def quit(self):
            return None

    def fake_init_driver(self):
        self.driver = DummyDriver()
        self.service = None

    monkeypatch.setattr(SeleniumContentLoader, "_init_driver", fake_init_driver)

    loader = SeleniumContentLoader(timeout=1, headless=True)

    with pytest.raises(ContentNotLoadedException) as exc_info:
        loader.load_content(LIVE_HTML_URL)

    assert "Unexpected error while loading page" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, RuntimeError)


@pytest.mark.integration
def test_selenium_loader_returns_page_source_from_real_website():
    loader = build_loader(timeout=30)

    try:
        page_source = loader.load_content(LIVE_HTML_URL)
    finally:
        loader.close()

    assert "<html" in page_source.lower()
    assert "example domain" in page_source.lower()


@pytest.mark.integration
def test_selenium_loader_wraps_invalid_urls_with_real_driver():
    loader = build_loader(timeout=30)

    try:
        with pytest.raises(BadURLException):
            loader.load_content("notaurl")
    finally:
        loader.close()


@pytest.mark.integration
def test_selenium_loader_wraps_timeouts_against_real_website():
    loader = build_loader(timeout=1)
    loader.driver.set_page_load_timeout(0.001)

    try:
        with pytest.raises(TimeoutException):
            loader.load_content(SLOW_RESPONSE_URL)
    finally:
        loader.close()


@pytest.mark.integration
def test_selenium_loader_close_releases_real_driver_and_service():
    loader = build_loader(timeout=30)
    service = loader.service

    loader.close()

    assert service.is_connectable() is False
    assert service.process is None or service.process.poll() is not None
