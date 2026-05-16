import pytest

from scraperkit.base.base_content_loader import BaseContentLoader
from scraperkit.base.base_scraper import BaseScraper
from scraperkit.exceptions import (
    BadURLException,
    ContentNotLoadedException,
    DataComponentNotFoundException,
    DataParsingException,
    DriverNotInitializedException,
    RateLimitException,
    TimeoutException,
)


class ConcreteLoader(BaseContentLoader):
    def load_content(self, page_url):
        return f"<html>{page_url}</html>"


class ConcreteScraper(BaseScraper):
    def get_page_content(self, page_url):
        return f"<html>{page_url}</html>"

    def get_pagination_details(self, page_url):
        return {"current_page": 1, "total_pages": 1, "next_page_url": None}

    def get_product_listings(self, listings_page_url, page=1):
        return [f"{listings_page_url}?page={page}"]

    def get_product_details(self, product_page_url):
        return {"url": product_page_url}


@pytest.mark.unit
def test_base_content_loader_has_default_headers():
    loader = ConcreteLoader()

    assert "User-Agent" in loader.headers
    assert loader.timeout == 10


@pytest.mark.unit
def test_base_scraper_initializes_shared_state():
    scraper = ConcreteScraper(
        base_url="https://example.com/",
        headers={"X-Test": "1"},
        content_loader="loader",
    )

    assert scraper.base_url == "https://example.com/"
    assert scraper.headers == {"X-Test": "1"}
    assert scraper.content_loader == "loader"
    assert scraper.current_page_content is None
    assert scraper.current_product_page_content is None


@pytest.mark.unit
def test_base_classes_are_abstract():
    with pytest.raises(TypeError):
        BaseContentLoader()

    with pytest.raises(TypeError):
        BaseScraper("https://example.com/")


@pytest.mark.unit
def test_scraperkit_exceptions_are_regular_exceptions():
    exception_types = [
        BadURLException,
        ContentNotLoadedException,
        DataComponentNotFoundException,
        DataParsingException,
        DriverNotInitializedException,
        RateLimitException,
        TimeoutException,
    ]

    for exception_type in exception_types:
        assert issubclass(exception_type, Exception)
