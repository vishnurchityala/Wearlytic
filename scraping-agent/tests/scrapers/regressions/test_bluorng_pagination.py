import pytest

from scraperkit.scrapers.bluorng_scraper import BluOrngScraper
from tests.scrapers.regressions._helpers import RecordingPageLoader


BLUORNG_PAGE_1_URL = "https://bluorng.com/collections/t-shirts"
BLUORNG_PAGE_2_URL = "https://bluorng.com/collections/t-shirts?page=2"
BLUORNG_PAGE_10_URL = "https://bluorng.com/collections/t-shirts?page=10"


def bluorng_pagination_html(current_page_markup: str, links_markup: str) -> str:
    return f"""
    <div class="pagination-wrapper">
      <nav class="pagination" aria-label="Pagination">
        {current_page_markup}
        {links_markup}
      </nav>
    </div>
    """


def bluorng_listing_html(extra_html: str = "") -> str:
    return f"""
    <div class="card__content">
      <a href="/products/black-frozen-claw-t-shirt">Black Frozen Claw T-Shirt</a>
    </div>
    <div class="card__content">
      <a href="/products/blu-dragonfly-t-shirt">Blu Dragonfly T-Shirt</a>
    </div>
    <div class="card__content">
      <a href="/products/black-frozen-claw-t-shirt">Duplicate Product</a>
    </div>
    {extra_html}
    """


@pytest.mark.unit
def test_bluorng_pagination_reads_next_page_from_bottom_links():
    loader = RecordingPageLoader(
        default_html=bluorng_pagination_html(
            current_page_markup="<span>1</span>",
            links_markup="""
            <a href="/collections/t-shirts?page=2">2</a>
            <a href="/collections/t-shirts?page=3">3</a>
            <span>...</span>
            <a href="/collections/t-shirts?page=10">10</a>
            """,
        )
    )
    scraper = BluOrngScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(BLUORNG_PAGE_1_URL)

    assert pagination == {
        "current_page": 1,
        "total_pages": 10,
        "next_page_url": BLUORNG_PAGE_2_URL,
    }


@pytest.mark.unit
def test_bluorng_pagination_follows_parsed_next_page_url():
    current_url = "https://bluorng.com/collections/t-shirts?sort_by=manual&page=2"
    expected_next_url = "https://bluorng.com/collections/t-shirts?sort_by=manual&page=3"
    loader = RecordingPageLoader(
        default_html=bluorng_pagination_html(
            current_page_markup="<span>2</span>",
            links_markup="""
            <a href="/collections/t-shirts?sort_by=manual&page=1">1</a>
            <a href="/collections/t-shirts?sort_by=manual&page=3">3</a>
            <span>...</span>
            <a href="/collections/t-shirts?sort_by=manual&page=10">10</a>
            """,
        )
    )
    scraper = BluOrngScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(current_url)

    assert pagination == {
        "current_page": 2,
        "total_pages": 10,
        "next_page_url": expected_next_url,
    }


@pytest.mark.unit
def test_bluorng_pagination_returns_no_next_page_on_final_page():
    loader = RecordingPageLoader(
        default_html=bluorng_pagination_html(
            current_page_markup="<span>10</span>",
            links_markup="""
            <a href="/collections/t-shirts?page=1">1</a>
            <span>...</span>
            <a href="/collections/t-shirts?page=9">9</a>
            """,
        )
    )
    scraper = BluOrngScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(BLUORNG_PAGE_10_URL)

    assert pagination == {
        "current_page": 10,
        "total_pages": 10,
        "next_page_url": None,
    }


@pytest.mark.unit
def test_bluorng_pagination_treats_missing_pagination_as_single_page():
    loader = RecordingPageLoader(default_html=bluorng_listing_html())
    scraper = BluOrngScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(BLUORNG_PAGE_1_URL)

    assert pagination == {
        "current_page": 1,
        "total_pages": 1,
        "next_page_url": None,
    }


@pytest.mark.unit
def test_bluorng_listing_extraction_uses_resolved_page_url_and_cached_content():
    page_html = bluorng_listing_html(
        extra_html=bluorng_pagination_html(
            current_page_markup="<span>2</span>",
            links_markup='<a href="/collections/t-shirts?page=3">3</a>',
        )
    )
    loader = RecordingPageLoader(html_by_url={BLUORNG_PAGE_2_URL: page_html})
    scraper = BluOrngScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(BLUORNG_PAGE_2_URL)
    listings = scraper.get_product_listings(BLUORNG_PAGE_2_URL, page=2)

    assert loader.requested_urls == [BLUORNG_PAGE_2_URL]
    assert pagination["next_page_url"] == "https://bluorng.com/collections/t-shirts?page=3"
    assert listings == [
        "https://bluorng.com/products/black-frozen-claw-t-shirt",
        "https://bluorng.com/products/blu-dragonfly-t-shirt",
    ]
