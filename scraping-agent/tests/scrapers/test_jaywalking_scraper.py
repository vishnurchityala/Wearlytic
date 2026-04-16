import pytest

from scraperkit import SCRAPER_URL_MAP
from tests.scrapers._helpers import run_live_scraper_case


JAYWALKING_LISTING_URL = "https://www.jaywalking.in/collections/t-shirt"


@pytest.mark.integration
def test_jaywalking_scraper_extracts_listing_and_product_data_from_real_website(
    request,
    scraper_test_artifact_root,
):
    run_live_scraper_case(
        request=request,
        scraper_test_artifact_root=scraper_test_artifact_root,
        source_name="jaywalking",
        scraper_cls=SCRAPER_URL_MAP["jaywalking"],
        listing_url=JAYWALKING_LISTING_URL,
    )
