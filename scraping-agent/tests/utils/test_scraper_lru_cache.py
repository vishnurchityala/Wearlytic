import pytest

from scraperkit.base import BaseScraper
from scraperkit.utils.scraper_lru_cache import ScraperLRUCache


class DummyScraper(BaseScraper):
    def __init__(self, source_name):
        super().__init__(f"https://{source_name}.example/")
        self.source_name = source_name
        self.close_calls = 0

    def get_page_content(self, page_url):
        return page_url

    def get_pagination_details(self, page_url):
        return {}

    def get_product_listings(self, listings_page_url, page=1):
        return []

    def get_product_details(self, product_page_url):
        return {}

    def close(self):
        self.close_calls += 1
        super().close()


@pytest.mark.unit
def test_cache_returns_most_recent_scraper_for_a_source():
    cache = ScraperLRUCache(max_size=3)
    first = DummyScraper("amazon")
    second = DummyScraper("amazon")

    cache.insert("amazon", first)
    cache.insert("amazon", second)

    assert cache.get("amazon") is second
    assert cache.get("amazon") is first
    assert cache.get("amazon") is None


@pytest.mark.unit
def test_cache_evicts_oldest_scraper_when_max_size_is_exceeded():
    cache = ScraperLRUCache(max_size=2)
    amazon = DummyScraper("amazon")
    myntra = DummyScraper("myntra")
    bluorng = DummyScraper("bluorng")

    cache.insert("amazon", amazon)
    cache.insert("myntra", myntra)
    cache.insert("bluorng", bluorng)

    assert cache.get("amazon") is None
    assert cache.get("myntra") is myntra
    assert cache.get("bluorng") is bluorng


@pytest.mark.unit
def test_cache_closes_evicted_scraper_when_max_size_is_exceeded():
    cache = ScraperLRUCache(max_size=2)
    amazon = DummyScraper("amazon")
    myntra = DummyScraper("myntra")
    bluorng = DummyScraper("bluorng")

    cache.insert("amazon", amazon)
    cache.insert("myntra", myntra)
    cache.insert("bluorng", bluorng)

    assert amazon.close_calls == 1
    assert myntra.close_calls == 0
    assert bluorng.close_calls == 0
