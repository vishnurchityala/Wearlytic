import pytest

import scraperkit
import scraperkit.utils as scraper_utils
from scraperkit.base import BaseScraper
from scraperkit.exceptions import BadURLException
from scraperkit.utils import ScraperLRUCache, extract_domain, get_driver_path, get_scraper_from_url


class DummyScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://dummy.example/")

    def get_page_content(self, page_url):
        return page_url

    def get_pagination_details(self, page_url):
        return {}

    def get_product_listings(self, listings_page_url, page=1):
        return []

    def get_product_details(self, product_page_url):
        return {}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("url", "expected_domain"),
    [
        ("https://www.amazon.in/dp/B0TEST1234", "amazon"),
        ("https://www.myntra.com/men-tshirts", "myntra"),
        ("https://www.thesouledstore.com/men/t-shirts", "thesouledstore"),
    ],
)
def test_extract_domain_returns_supported_source_name(url, expected_domain):
    assert extract_domain(url) == expected_domain


@pytest.mark.unit
def test_get_scraper_from_url_uses_cache_when_available(monkeypatch):
    cache = ScraperLRUCache(max_size=2)
    cached_scraper = DummyScraper()
    cache.insert("dummyshop", cached_scraper)

    monkeypatch.setattr(scraper_utils, "cache", cache)
    monkeypatch.setattr(scraperkit, "SCRAPER_URL_MAP", {"dummyshop": DummyScraper})

    scraper = get_scraper_from_url("https://www.dummyshop.com/products/test-item")

    assert scraper is cached_scraper
    assert cache.get("dummyshop") is None


@pytest.mark.unit
def test_get_scraper_from_url_creates_new_scraper_when_cache_is_empty(monkeypatch):
    cache = ScraperLRUCache(max_size=2)
    monkeypatch.setattr(scraper_utils, "cache", cache)
    monkeypatch.setattr(scraperkit, "SCRAPER_URL_MAP", {"dummyshop": DummyScraper})

    scraper = get_scraper_from_url("https://dummyshop.com/products/test-item")

    assert isinstance(scraper, DummyScraper)


@pytest.mark.unit
def test_get_scraper_from_url_raises_for_unsupported_sources(monkeypatch):
    monkeypatch.setattr(scraperkit, "SCRAPER_URL_MAP", {})

    with pytest.raises(BadURLException):
        get_scraper_from_url("https://unsupported.example.com/item")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("platform", "expected_suffix"),
    [
        ("macosarm64", "chromedriver-mac-arm64/chromedriver"),
        ("macosamd64", "chromedriver-mac-x64/chromedriver"),
        ("win64", "chromedriver-win64/chromedriver.exe"),
        ("linux64", "chromedriver-linux64/chromedriver"),
    ],
)
def test_get_driver_path_matches_platform(monkeypatch, platform, expected_suffix):
    monkeypatch.setenv("PLATFORM", platform)

    assert get_driver_path().endswith(expected_suffix)
