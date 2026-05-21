# ScraperKit

A modular web scraping framework designed for fast and easy API usage conversion.

## Architecture

<p align="center">
  <img src="../../assets/SCRAPER-KIT-ARCHITECTURE.png" alt="ScraperKit architecture" width="900" />
</p>

The current package implements base classes, content loaders, models,
exceptions, scraper implementations, and utility helpers. The proxy provider and
proxy manager boxes in the diagram are not present in the current package tree.

## Package Classes

### Base Package (`base/`)
- `BaseContentLoader`: Abstract base class for content loading
- `BaseScraper`: Abstract base class for scrapers

### Loaders Package (`loaders/`)
- `SeleniumContentLoader`: Selenium-based content loader
- `PlaywrightContentLoader`: Playwright-based content loader
- `RequestContentLoader`: Requests-based content loader
- `SeleniumInfinityScrollContentLoader`: Selenium-based scrollable content loader

### Exceptions Package (`exceptions/`)
- `BadURLException`: Invalid URL errors
- `ContentNotLoadedException`: Content loading failures
- `DataComponentNotFoundException`: Missing data elements
- `DataParsingException`: Parsing errors
- `RateLimitException`: Rate limiting
- `TimeoutException`: Timeout handling

### Models Package (`models/`)
- `Product`: Product data model

### Utils Package (`utils/`)
- `extract_domain`: Domain-key helper used by scraper lookup
- `get_driver_path`: Platform-specific ChromeDriver path resolver
- `get_scraper_from_url`: Scraper registry/cache lookup helper
- `ScraperLRUCache`: Source-aware scraper instance cache

### Scrapers Package (`scrapers/`)
- `AmazonScraper`: Amazon-specific scraper
- `BluOrngScraper`: BluOrng-specific scraper
- `JayWalkingScraper`: Jaywalking-specific scraper
- `MyntraScraper`: Myntra-specific scraper
- `SouledStoreScraper`: The Souled Store-specific scraper

## Sample Usage of Scrapers

```python
from scraperkit.loaders.selenium_content_loader import SeleniumContentLoader
from scraperkit.scrapers.amazon_scraper import AmazonScraper

# Initialize components
loader = SeleniumContentLoader(headless=True)
scraper = AmazonScraper(loader)

# Scrape product data
product_data = scraper.get_product_details("https://amazon.com/product/123")
print(product_data)
```
### Sample Usage of Loaders
```python
from scraperkit.loaders.selenium_content_loader import SeleniumContentLoader

# Initialize with custom settings
loader = SeleniumContentLoader(
    timeout=30,
    headless=True,
    headers={
        "User-Agent": "Custom User Agent",
        "Accept-Language": "en-US,en;q=0.9"
    }
)

# Load content
try:
    content = loader.load_content("https://example.com")
finally:
    loader.close()  # Cleanup resources
```

## Package Structure

```
scraperkit/
├── __init__.py
├── README.md
├── base/
│   ├── __init__.py
│   ├── base_content_loader.py
│   └── base_scraper.py
├── exceptions/
│   ├── __init__.py
│   ├── bad_url_exception.py
│   ├── content_not_loaded_exception.py
│   ├── data_component_not_found_exception.py
│   ├── data_parsing_exception.py
│   ├── rate_limit_exception.py
│   └── timeout_exception.py
├── loaders/
│   ├── __init__.py
│   ├── playwright_content_loader.py
│   ├── request_content_loader.py
│   ├── selenium_content_loader.py
│   └── selenium_infinity_scroll_content_loader.py
├── models/
│   ├── __init__.py
│   └── product.py
├── utils/
│   ├── __init__.py
│   └── scraper_lru_cache.py
└── scrapers/
    ├── __init__.py
    ├── amazon_scraper.py
    ├── bluorng_scraper.py
    ├── jaywalking_scraper.py
    ├── myntra_scraper.py
    └── souled_store_scraper.py
```
