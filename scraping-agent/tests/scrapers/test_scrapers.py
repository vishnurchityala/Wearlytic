from datetime import datetime, timezone

import pytest

from api.models.job import JobResult
from api.models.listing import Listing, ListingItem
from api.models.product import Product as ApiProduct
from scraperkit import SCRAPER_URL_MAP
from scraperkit.models import Product as ScraperProduct
from tests.scrapers.scrape_artifact_logger import ScrapeArtifactLogger


DEFAULT_LISTING_URLS = {
    "amazon": "https://www.amazon.in/s?k=men+t-shirts",
    "myntra": "https://www.myntra.com/mens-tshirts",
    "bluorng": "https://bluorng.com/collections/polos",
    "jaywalking": "https://www.jaywalking.in/collections/t-shirt",
    "thesouledstore": "https://www.thesouledstore.com/men-classic-tshirts",
}


SCRAPER_CASES = [
    (source_name, scraper_cls, DEFAULT_LISTING_URLS[source_name])
    for source_name, scraper_cls in SCRAPER_URL_MAP.items()
    if source_name in DEFAULT_LISTING_URLS
]


def assert_valid_pagination_payload(pagination):
    assert isinstance(pagination, dict)
    assert set(pagination.keys()) == {
        "current_page",
        "total_pages",
        "next_page_url",
    }

    if pagination["total_pages"] is not None:
        assert isinstance(pagination["total_pages"], int)
        assert pagination["total_pages"] >= 1

    if pagination["next_page_url"] is not None:
        assert isinstance(pagination["next_page_url"], str)
        assert pagination["next_page_url"].startswith("http")


def assert_valid_product_payload(product):
    assert isinstance(product, ScraperProduct)
    assert product.id.strip()
    assert product.title.strip()
    assert product.price > 0
    assert product.description.strip()
    assert str(product.url).startswith("http")
    assert str(product.image_url).startswith("http")
    assert product.page_content

    if product.category is not None:
        assert product.category.strip()

    if product.gender is not None:
        assert product.gender.strip()

    if product.rating is not None:
        assert 0 <= product.rating <= 5

    if product.review_count is not None:
        assert product.review_count >= 0

    if product.sizes is not None:
        assert all(size.strip() for size in product.sizes)

    if product.colors is not None:
        assert all(color.strip() for color in product.colors)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("source_name", "scraper_cls", "listing_url"),
    SCRAPER_CASES,
    ids=[case[0] for case in SCRAPER_CASES],
)
def test_scrapers_extract_listing_and_product_data_from_real_websites(
    request,
    scraper_test_artifact_root,
    source_name,
    scraper_cls,
    listing_url,
):
    scraper = scraper_cls()
    artifact_logger = ScrapeArtifactLogger(
        artifact_root=scraper_test_artifact_root,
        source_name=source_name,
        scraper_name=scraper_cls.__name__,
        test_nodeid=request.node.nodeid,
        listing_url=listing_url,
    )
    artifact_logger.attach_to_scraper(scraper)
    current_stage = "scraper_initialization"

    try:
        current_stage = "pagination"
        pagination = scraper.get_pagination_details(listing_url)
        artifact_logger.record_pagination(pagination)

        current_stage = "listing_extraction"
        listings = scraper.get_product_listings(listing_url)
        artifact_logger.record_listings(listings)
        assert listings, f"{source_name} returned no product listings for {listing_url}"

        current_stage = "product_extraction"
        product_url = listings[0]
        product = scraper.get_product_details(product_url)
        artifact_logger.record_product(product)
    except Exception as exc:
        artifact_logger.record_error(current_stage, exc)
        artifact_logger.finalize(status="failed")
        raise
    finally:
        scraper.close()
        if artifact_logger.summary["status"] == "running":
            artifact_logger.finalize(status="completed")

    assert_valid_pagination_payload(pagination)
    assert isinstance(listings, list)
    assert listings
    assert all(url.startswith("http") for url in listings)
    assert len(listings) == len(set(listings))
    assert_valid_product_payload(product)

    listing_payload = Listing(
        items=[
            ListingItem(url=url, page_rank=index)
            for index, url in enumerate(listings, start=1)
        ]
    )
    product_payload = JobResult(
        job_id=f"{source_name}-product-live",
        result=product.model_dump(mode="json"),
        status="completed",
        completed_at=datetime.now(timezone.utc),
        error_message=None,
    )
    listing_result = JobResult(
        job_id=f"{source_name}-listing-live",
        result=listing_payload.model_dump(mode="json"),
        status="completed",
        completed_at=datetime.now(timezone.utc),
        error_message=None,
    )

    assert isinstance(product_payload.result, ApiProduct)
    assert str(product_payload.result.url).startswith("http")
    assert product_payload.result.page_content
    assert len(listing_result.result.items) == len(listings)
