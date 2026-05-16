import pytest

from tests.scrapers._helpers import run_live_scraper_case
from tests.scrapers.cases import SCRAPER_TEST_CASES


@pytest.mark.integration
@pytest.mark.parametrize(
    "scraper_case",
    SCRAPER_TEST_CASES,
    ids=[scraper_case.source_name for scraper_case in SCRAPER_TEST_CASES],
)
def test_scraper_extracts_listing_and_product_data_from_live_website(
    request,
    scraper_test_artifact_root,
    scraper_case,
):
    run_live_scraper_case(
        request=request,
        scraper_test_artifact_root=scraper_test_artifact_root,
        scraper_case=scraper_case,
    )
