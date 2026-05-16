from urllib.parse import urlparse

import pytest

from scraperkit import SCRAPER_URL_MAP
from scraperkit.base.base_scraper import BaseScraper
from tests.scrapers.cases import SCRAPER_TEST_CASES


@pytest.mark.unit
def test_scraper_manifest_covers_all_registered_scrapers():
    assert {scraper_case.source_name for scraper_case in SCRAPER_TEST_CASES} == set(
        SCRAPER_URL_MAP
    )


@pytest.mark.unit
def test_scraper_manifest_contains_concrete_scraper_classes_and_absolute_urls():
    for scraper_case in SCRAPER_TEST_CASES:
        assert issubclass(scraper_case.scraper_cls, BaseScraper)
        assert SCRAPER_URL_MAP[scraper_case.source_name] is scraper_case.scraper_cls

        parsed_url = urlparse(scraper_case.listing_url)
        assert parsed_url.scheme in {"http", "https"}
        assert parsed_url.netloc
