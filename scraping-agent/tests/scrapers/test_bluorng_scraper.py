import pytest

from scraperkit import SCRAPER_URL_MAP
from tests.scrapers._helpers import run_live_scraper_case


BLUORNG_LISTING_URL = "https://bluorng.com/collections/polos"


@pytest.mark.integration
def test_bluorng_scraper_extracts_listing_and_product_data_from_real_website(
    request,
    scraper_test_artifact_root,
):
    run_live_scraper_case(
        request=request,
        scraper_test_artifact_root=scraper_test_artifact_root,
        source_name="bluorng",
        scraper_cls=SCRAPER_URL_MAP["bluorng"],
        listing_url=BLUORNG_LISTING_URL,
    )
