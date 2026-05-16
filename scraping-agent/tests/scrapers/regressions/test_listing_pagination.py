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
