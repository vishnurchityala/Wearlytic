import pytest

from scraperkit.scrapers.amazon_scraper import AmazonScraper
from scraperkit.scrapers.myntra_scraper import MyntraScraper
from tests.scrapers.regressions._helpers import RecordingPageLoader


AMAZON_PAGE_2_URL = "https://www.amazon.in/s?k=men+t-shirts&page=2"
AMAZON_LISTING_HTML = """
<div data-component-type="s-search-results">
  <div data-component-type="s-search-result" data-asin="B0D25JKGJP"></div>
</div>
"""

MYNTRA_PAGE_2_URL = "https://www.myntra.com/mens-tshirts?p=2"
MYNTRA_LISTING_HTML = """
<ul>
  <li class="product-base">
    <a href="/tshirts/example-product"></a>
  </li>
</ul>
"""


def myntra_pagination_html(current_page: int, total_pages: int, current_url: str) -> str:
    return f"""
    <link rel="canonical" href="{current_url}" />
    <li class="pagination-paginationMeta">Page {current_page} of {total_pages}</li>
    """


@pytest.mark.unit
def test_amazon_get_product_listings_uses_resolved_page_url_without_reappending_page():
    loader = RecordingPageLoader(html_by_url={AMAZON_PAGE_2_URL: AMAZON_LISTING_HTML})
    scraper = AmazonScraper(content_loader=loader)

    listings = scraper.get_product_listings(AMAZON_PAGE_2_URL, page=2)

    assert loader.requested_urls == [AMAZON_PAGE_2_URL]
    assert listings == ["https://www.amazon.in/dp/B0D25JKGJP"]


@pytest.mark.unit
def test_myntra_get_product_listings_uses_resolved_page_url_without_reappending_page():
    loader = RecordingPageLoader(html_by_url={MYNTRA_PAGE_2_URL: MYNTRA_LISTING_HTML})
    scraper = MyntraScraper(content_loader=loader)

    listings = scraper.get_product_listings(MYNTRA_PAGE_2_URL, page=2)

    assert loader.requested_urls == [MYNTRA_PAGE_2_URL]
    assert listings == ["https://www.myntra.com/tshirts/example-product"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("current_page", "total_pages", "current_url", "expected_next_url"),
    [
        (
            1,
            30,
            "https://www.myntra.com/mens-tshirts",
            "https://www.myntra.com/mens-tshirts?p=2",
        ),
        (
            9,
            30,
            "https://www.myntra.com/mens-tshirts?p=9",
            "https://www.myntra.com/mens-tshirts?p=10",
        ),
        (
            10,
            30,
            "https://www.myntra.com/mens-tshirts?p=10",
            None,
        ),
        (
            5,
            5,
            "https://www.myntra.com/mens-tshirts?p=5",
            None,
        ),
    ],
)
def test_myntra_pagination_stops_at_page_cap_or_real_final_page(
    current_page,
    total_pages,
    current_url,
    expected_next_url,
):
    loader = RecordingPageLoader(
        default_html=myntra_pagination_html(
            current_page=current_page,
            total_pages=total_pages,
            current_url=current_url,
        )
    )
    scraper = MyntraScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(current_url)

    assert pagination == {
        "current_page": current_page,
        "total_pages": total_pages,
        "next_page_url": expected_next_url,
    }
