# Scraper Creation Guide

This guide documents the expected workflow for adding a new source scraper to
`scraperkit`. Keep new scrapers compatible with the current class-based
registry until the planned config-driven factory migration is implemented.

## Before You Code

1. Pick one representative listing URL and one representative product URL for
   the source.
2. Load both pages with the simplest content loader that can render the content.
   Use `RequestContentLoader` only when static HTML is enough. Use
   `SeleniumContentLoader`, `SeleniumInfinityScrollContentLoader`, or
   `PlaywrightContentLoader` when product cards or product details are rendered
   by client-side JavaScript.
3. Inspect the rendered HTML for stable selectors:
   - Listing grid root and product-card root.
   - Product anchor selectors and duplicate links.
   - Pagination links or infinite-scroll boundaries.
   - Product title, price, image, description, variants, rating, and review
     count.
4. Prefer page-scoped selectors over global anchors. Navigation menus and
   recommendation widgets often contain product links that should not be part of
   listing extraction.

Example Selenium inspection snippet:

```python
from bs4 import BeautifulSoup
from scraperkit.loaders import SeleniumContentLoader

loader = SeleniumContentLoader(timeout=45, headless=True)

try:
    html = loader.load_content("https://example.com/collections/example")
    soup = BeautifulSoup(html, "html.parser")

    print("title:", soup.title.get_text(strip=True) if soup.title else None)
    print("product cards:", len(soup.select("product-card, .product-card")))
    print("product links:")
    for link in soup.select("main a[href*='/products/']")[:20]:
        print(link.get("href"), link.get_text(" ", strip=True))
finally:
    loader.close()
```

## File And Class Shape

Create one source-specific module under `scraperkit/scrapers/`:

```text
scraperkit/scrapers/example_scraper.py
```

The scraper class must extend `BaseScraper` and accept injectable dependencies:

```python
from bs4 import BeautifulSoup

from scraperkit.base import BaseScraper
from scraperkit.exceptions import (
    ContentNotLoadedException,
    DataComponentNotFoundException,
    DataParsingException,
)
from scraperkit.loaders import SeleniumContentLoader
from scraperkit.models import Product


class ExampleScraper(BaseScraper):
    def __init__(self, headers=None, content_loader=None):
        super().__init__("https://example.com/", headers=headers or {})
        self.id_prefix = "example_"
        self.content_loader = content_loader or SeleniumContentLoader(headers=headers)
```

Constructor rules:

1. Accept `headers=None` and `content_loader=None`.
2. Pass a source base URL to `BaseScraper`.
3. Use `headers or {}` unless a site requires default browser headers.
4. Set a stable `id_prefix`.
5. Let tests inject `RecordingPageLoader` or another static loader through
   `content_loader`.

## Required Methods

Every scraper must implement the `BaseScraper` public contract:

| Method | Requirement |
| --- | --- |
| `get_page_content(page_url)` | Return loaded HTML or raise `ContentNotLoadedException`. |
| `get_pagination_details(page_url)` | Return `current_page`, `total_pages`, and `next_page_url`. |
| `get_product_listings(listings_page_url, page=1)` | Return unique absolute product URLs from the listing page. |
| `get_product_details(product_page_url)` | Return a `scraperkit.models.Product` object. |

The pagination payload must always have exactly these keys:

```python
{
    "current_page": 1,
    "total_pages": 1,
    "next_page_url": None,
}
```

Use `None` for `next_page_url` when the current listing is the final page or
pagination is not present.

## Listing Extraction Rules

Listing extraction must:

1. Load the exact `listings_page_url` it receives. Do not append another page
   query parameter when the caller has already resolved a next-page URL.
2. Scope extraction to the listing grid or search-results root.
3. Return absolute URLs.
4. De-duplicate repeated links while preserving page order.
5. Raise `DataComponentNotFoundException` when the expected listing container or
   product cards are missing.
6. Raise `DataParsingException` when product cards exist but no valid product
   URLs can be parsed.

When `get_pagination_details()` and `get_product_listings()` parse the same URL,
cache the listing HTML on the scraper instance so the page is loaded once:

```python
def _get_listing_page_content(self, page_url):
    if page_url == self._current_listing_url and self.current_page_content:
        return self.current_page_content

    page_content = self.get_page_content(page_url)
    self._current_listing_url = page_url
    self.current_page_content = page_content
    return page_content
```

## Product Extraction Rules

`get_product_details()` must return `scraperkit.models.Product`.

Required fields:

| Field | Requirement |
| --- | --- |
| `id` | Stable source-prefixed ID. |
| `title` | Non-empty product title. |
| `price` | Positive numeric value. |
| `description` | Non-empty product description. |
| `url` | Direct product page URL. |
| `image_url` | Absolute product image URL. |

Recommended optional fields:

| Field | Notes |
| --- | --- |
| `category` | Prefer structured metadata, breadcrumbs, or URL-derived category. |
| `gender` | Use page metadata, title, description, breadcrumbs, or URL hints. |
| `colors` | Parse variant values or swatches. Use `[]` when none are available. |
| `sizes` | Parse available variant values. Use `[]` when none are available. |
| `material` | Parse material, composition, or fabric text when present. |
| `rating` | Return `0.0` when unavailable. |
| `review_count` | Return `0` when unavailable. |
| `page_content` | Store `soup.body.prettify()` when possible. |

Prefer structured data when the site provides it:

1. JSON-LD `Product`, `ProductGroup`, or `@graph`.
2. Open Graph and Twitter meta tags.
3. Semantic product containers and variant controls.
4. Breadcrumbs or canonical URLs.

Avoid brittle string slicing for page structure. Use BeautifulSoup selectors and
small parsing helpers for prices, counts, handles, and text cleanup.

## Exceptions

Use existing scraper exceptions so failed jobs are diagnosable:

| Exception | Use When |
| --- | --- |
| `ContentNotLoadedException` | The loader cannot fetch or render the page. |
| `DataComponentNotFoundException` | A required selector, component, or value is missing. |
| `DataParsingException` | A component exists but cannot be parsed into a valid value. |

Do not hide parser breakage by returning placeholder products. A scraper should
fail clearly when the source markup changes.

## Registration

Register a new scraper in three places:

1. Export the class from `scraperkit/scrapers/__init__.py`.
2. Add the domain key to `SCRAPER_URL_MAP` in `scraperkit/__init__.py`.
3. Add a live test case in `tests/scrapers/cases.py`.

The domain key must match `extract_domain(url)` from `scraperkit.utils`.

Examples:

| URL | Domain Key |
| --- | --- |
| `https://www.amazon.in/dp/...` | `amazon` |
| `https://www.myntra.com/...` | `myntra` |
| `https://offduty.in/collections/...` | `offduty` |

## Tests

Add focused regression tests for each new scraper:

1. Static listing extraction test with `RecordingPageLoader`.
2. Static pagination test when the source has multiple pages.
3. Static product extraction test with representative rendered HTML.
4. Manifest coverage by adding the scraper to `tests/scrapers/cases.py`.
5. Domain utility coverage when introducing a new domain pattern.

Useful commands:

```bash
venv/bin/pytest tests/scrapers/regressions/test_example_scraper.py
venv/bin/pytest tests/scrapers/test_scraper_manifest.py tests/utils/test_utils.py
venv/bin/pytest -m unit
venv/bin/pytest tests/scrapers/test_live_scraper_contract.py -k example
```

Live scraper tests require network access and Selenium-based tests require a
valid `PLATFORM` value so `get_driver_path()` can resolve the ChromeDriver.

## Completion Checklist

- [ ] Loaded sample listing and product pages through the selected content
      loader.
- [ ] Added `scraperkit/scrapers/<source>_scraper.py`.
- [ ] Implemented listing, pagination, and product extraction.
- [ ] Returned absolute product and image URLs.
- [ ] Raised scraperkit exceptions for load, missing-component, and parsing
      failures.
- [ ] Registered the scraper in `scraperkit/scrapers/__init__.py`.
- [ ] Registered the domain in `SCRAPER_URL_MAP`.
- [ ] Added or updated `tests/scrapers/cases.py`.
- [ ] Added regression tests with static HTML.
- [ ] Ran focused unit tests and a live scraper contract when feasible.
