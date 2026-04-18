import pytest

from scraperkit.exceptions import DataComponentNotFoundException, DataParsingException
from scraperkit.scrapers.myntra_scraper import MyntraScraper
from tests.scrapers.regressions._helpers import RecordingPageLoader


VALID_SINGLE_PAGE_HTML = """
<main class="search-base">
  <span class="title-count"> - 1 items </span>
  <div class="search-searchProductsContainer">
    <li class="product-base">
      <a href="/tshirts/example-product"></a>
    </li>
  </div>
</main>
"""

MALFORMED_PAGINATION_HTML = """
<main class="search-base">
  <span class="title-count"> - 1 items </span>
  <link rel="canonical" href="https://www.myntra.com/mens-tshirts" />
  <li class="pagination-paginationMeta">Page two of many</li>
  <div class="search-searchProductsContainer">
    <li class="product-base">
      <a href="/tshirts/example-product"></a>
    </li>
  </div>
</main>
"""

POSITIVE_COUNT_WITHOUT_PRODUCTS_HTML = """
<main class="search-base">
  <span class="title-count"> - 12 items </span>
  <div class="search-searchProductsContainer"></div>
</main>
"""

EMPTY_RESULTS_HTML = """
<main class="search-base">
  <span class="title-count"> - 0 items </span>
  <div class="search-searchProductsContainer"></div>
</main>
"""


@pytest.mark.unit
def test_myntra_missing_pagination_meta_is_treated_as_single_page_listing():
    scraper = MyntraScraper(content_loader=RecordingPageLoader(default_html=VALID_SINGLE_PAGE_HTML))

    pagination = scraper.get_pagination_details("https://www.myntra.com/mens-tshirts")
    listings = scraper.get_product_listings("https://www.myntra.com/mens-tshirts")

    assert pagination == {
        "current_page": 1,
        "total_pages": 1,
        "next_page_url": None,
    }
    assert listings == ["https://www.myntra.com/tshirts/example-product"]


@pytest.mark.unit
def test_myntra_malformed_pagination_meta_raises_parser_error():
    scraper = MyntraScraper(
        content_loader=RecordingPageLoader(default_html=MALFORMED_PAGINATION_HTML)
    )

    with pytest.raises(DataParsingException) as exc_info:
        scraper.get_pagination_details("https://www.myntra.com/mens-tshirts")

    assert "Unexpected Myntra pagination format" in str(exc_info.value)


@pytest.mark.unit
def test_myntra_missing_product_cards_with_positive_count_raises_component_error():
    scraper = MyntraScraper(
        content_loader=RecordingPageLoader(default_html=POSITIVE_COUNT_WITHOUT_PRODUCTS_HTML)
    )

    with pytest.raises(DataComponentNotFoundException) as exc_info:
        scraper.get_product_listings("https://www.myntra.com/mens-tshirts")

    assert "No Myntra product cards found" in str(exc_info.value)


@pytest.mark.unit
def test_myntra_zero_count_page_can_still_return_empty_listings():
    scraper = MyntraScraper(content_loader=RecordingPageLoader(default_html=EMPTY_RESULTS_HTML))

    listings = scraper.get_product_listings("https://www.myntra.com/mens-tshirts")

    assert listings == []
