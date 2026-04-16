import pytest

from scraperkit import SCRAPER_URL_MAP
from tests.scrapers._helpers import run_live_scraper_case


THESOULDEDSTORE_LISTING_URL = "https://www.thesouledstore.com/men-classic-tshirts"


@pytest.mark.integration
def test_thesouledstore_scraper_extracts_listing_and_product_data_from_real_website(
    request,
    scraper_test_artifact_root,
):
    run_live_scraper_case(
        request=request,
        scraper_test_artifact_root=scraper_test_artifact_root,
        source_name="thesouledstore",
        scraper_cls=SCRAPER_URL_MAP["thesouledstore"],
        listing_url=THESOULDEDSTORE_LISTING_URL,
    )
