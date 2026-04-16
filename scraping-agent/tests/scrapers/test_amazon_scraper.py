import pytest

from scraperkit import SCRAPER_URL_MAP
from tests.scrapers._helpers import run_live_scraper_case


AMAZON_LISTING_URL = "https://www.amazon.in/s?k=men+t-shirts"


@pytest.mark.integration
def test_amazon_scraper_extracts_listing_and_product_data_from_real_website(
    request,
    scraper_test_artifact_root,
):
    run_live_scraper_case(
        request=request,
        scraper_test_artifact_root=scraper_test_artifact_root,
        source_name="amazon",
        scraper_cls=SCRAPER_URL_MAP["amazon"],
        listing_url=AMAZON_LISTING_URL,
    )
