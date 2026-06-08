import pytest

from scraperkit.scrapers.offduty_scraper import OffDutyScraper
from tests.scrapers.regressions._helpers import RecordingPageLoader


LISTING_URL = "https://offduty.in/collections/collection-men"
LISTING_PAGE_2_URL = "https://offduty.in/collections/collection-men?page=2"
PRODUCT_URL = "https://offduty.in/products/blue-drift-bootcut-jeans?variant=41798574506081"


OFFDUTY_LISTING_HTML = """
<main>
  <a href="/products/navigation-featured">Navigation product that should be ignored</a>
  <ul class="product-grid product-grid--grid">
    <li class="product-grid__item">
      <product-card class="product-card">
        <a class="product-card__link" href="/products/blue-drift-bootcut-jeans?variant=41798574506081">
          Drift Bootcut Jeans
        </a>
        <a class="contents" href="/products/blue-drift-bootcut-jeans?variant=41798574506081"></a>
      </product-card>
    </li>
    <li class="product-grid__item">
      <product-card class="product-card">
        <a class="product-card__link" href="/products/classic-loose-straight-fit-jeans?variant=41798574866529">
          Classic Loose Straight Fit Jeans
        </a>
      </product-card>
    </li>
  </ul>
  <nav class="pagination" aria-label="Pagination">
    <a href="/collections/collection-men?page=2">2</a>
    <a href="/collections/collection-men?page=3">3</a>
    <a href="/collections/collection-men?page=7">7</a>
  </nav>
</main>
"""


OFFDUTY_PRODUCT_HTML = """
<html>
  <head>
    <link rel="canonical" href="https://offduty.in/products/blue-drift-bootcut-jeans" />
    <meta property="og:title" content="Drift Bootcut Jeans" />
    <meta property="og:description" content="Men's bootcut jeans. Composition : 100% Cotton" />
    <meta property="og:image:secure_url" content="https://offduty.in/cdn/shop/files/IMG_4594.png?v=1774675710" />
    <meta property="og:price:amount" content="1,850.00" />
    <script type="application/ld+json">
      {
        "@context": "http://schema.org/",
        "@type": "ProductGroup",
        "category": "Pants",
        "description": "Timeless Blue, Modern Edge. Men's bootcut jeans. Composition : 100% Cotton",
        "name": "Drift Bootcut Jeans"
      }
    </script>
    <script type="application/ld+json">
      {
        "@context": "http://schema.org",
        "@type": "Product",
        "name": "Drift Bootcut Jeans",
        "aggregateRating": {
          "@type": "AggregateRating",
          "ratingValue": 4.51,
          "reviewCount": 546
        }
      }
    </script>
  </head>
  <body>
    <div class="product-information">
      <h1>Drift Bootcut Jeans</h1>
      <product-price class="rte">Rs. 1,850.00</product-price>
      <fieldset class="variant-option">
        <legend>Color</legend>
        <input name="Color-template" value="Blue" checked />
        <input name="Color-template" value="Ash Grey" />
      </fieldset>
      <fieldset class="variant-option">
        <legend>Size</legend>
        <input name="Size-template" value="30" />
        <input name="Size-template" value="32" />
        <input name="Size-template" value="34" disabled />
      </fieldset>
      <details class="details">
        <summary>Description</summary>
        Timeless Blue, Modern Edge. Men's bootcut jeans. Composition : 100% Cotton
      </details>
    </div>
  </body>
</html>
"""


@pytest.mark.unit
def test_offduty_listing_extraction_uses_product_grid_and_cached_content():
    loader = RecordingPageLoader(html_by_url={LISTING_URL: OFFDUTY_LISTING_HTML})
    scraper = OffDutyScraper(content_loader=loader)

    pagination = scraper.get_pagination_details(LISTING_URL)
    listings = scraper.get_product_listings(LISTING_URL)

    assert loader.requested_urls == [LISTING_URL]
    assert pagination == {
        "current_page": 1,
        "total_pages": 7,
        "next_page_url": LISTING_PAGE_2_URL,
    }
    assert listings == [
        "https://offduty.in/products/blue-drift-bootcut-jeans?variant=41798574506081",
        "https://offduty.in/products/classic-loose-straight-fit-jeans?variant=41798574866529",
    ]


@pytest.mark.unit
def test_offduty_product_extraction_uses_rendered_product_metadata():
    loader = RecordingPageLoader(html_by_url={PRODUCT_URL: OFFDUTY_PRODUCT_HTML})
    scraper = OffDutyScraper(content_loader=loader)

    product = scraper.get_product_details(PRODUCT_URL)

    assert product.id == "offduty_blue_drift_bootcut_jeans"
    assert product.title == "Drift Bootcut Jeans"
    assert product.price == 1850.0
    assert product.category == "Pants"
    assert product.gender == "Men"
    assert str(product.image_url) == "https://offduty.in/cdn/shop/files/IMG_4594.png?v=1774675710"
    assert product.colors == ["Blue", "Ash Grey"]
    assert product.sizes == ["30", "32"]
    assert product.material == "100% Cotton"
    assert "Composition : 100% Cotton" in product.description
    assert product.rating == 4.51
    assert product.review_count == 546
    assert product.page_content
