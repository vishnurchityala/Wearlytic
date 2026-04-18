import pytest

from scraperkit.scrapers.amazon_scraper import AmazonScraper
from tests.scrapers.regressions._helpers import RecordingPageLoader


LISTING_URL = "https://www.amazon.in/s?k=men+t-shirts"

AMAZON_LISTING_HTML = """
<span data-component-type="s-search-results">
  <div class="s-main-slot s-result-list s-search-results sg-row">
    <div class="s-result-item s-widget s-widget-spacing-large AdHolder" data-asin=""></div>
    <div
      role="listitem"
      data-asin="B06Y2C9TSR"
      data-component-type="s-search-result"
      class="s-result-item s-asin"
    >
      <a href="/Some-Product/dp/B06Y2C9TSR/ref=sr_1_1"></a>
    </div>
    <div
      role="listitem"
      data-asin="B071YST7GM"
      class="s-result-item s-asin"
    >
      <a href="/Other-Product/dp/B071YST7GM/ref=sr_1_2"></a>
    </div>
  </div>
</span>
"""


@pytest.mark.unit
def test_amazon_get_product_listings_extracts_asins_from_current_result_markup():
    scraper = AmazonScraper(
        content_loader=RecordingPageLoader(html_by_url={LISTING_URL: AMAZON_LISTING_HTML})
    )

    listings = scraper.get_product_listings(LISTING_URL)

    assert listings == [
        "https://www.amazon.in/dp/B06Y2C9TSR",
        "https://www.amazon.in/dp/B071YST7GM",
    ]


@pytest.mark.unit
def test_amazon_reuses_cached_listing_page_between_pagination_and_listing_extraction():
    loader = RecordingPageLoader(html_by_url={LISTING_URL: AMAZON_LISTING_HTML})
    scraper = AmazonScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(LISTING_URL)
    listings = scraper.get_product_listings(LISTING_URL)

    assert pagination["current_page"] is None
    assert loader.requested_urls == [LISTING_URL]
    assert listings == [
        "https://www.amazon.in/dp/B06Y2C9TSR",
        "https://www.amazon.in/dp/B071YST7GM",
    ]
