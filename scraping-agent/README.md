# Scraping Agent

![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814a)
![Redis](https://img.shields.io/badge/Redis-dc382d?logo=redis&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47a248?logo=mongodb&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43b02a?logo=selenium&logoColor=white)

The scraping agent runs website-specific listing and product scrapers for Wearlytic.

## Responsibility

- Accept scrape job requests from internal services.
- Queue product and listing scrape tasks with Celery.
- Run site-specific scrapers from `scraperkit/scrapers/`.
- Store scrape job metadata and results.
- Expose status and result endpoints for asynchronous jobs.

## Supported Scrapers

Current scraper implementations live in `scraperkit/scrapers/` and include:

- Amazon
- BluOrng
- Jaywalking
- Myntra
- The Souled Store

## Scraper Implementation Contract

Every website scraper must be a concrete class under `scraperkit/scrapers/`
that extends `scraperkit.base.BaseScraper`.

Use this shape:

```python
from bs4 import BeautifulSoup

from scraperkit.base import BaseScraper
from scraperkit.loaders import RequestContentLoader
from scraperkit.models import Product


class ExampleScraper(BaseScraper):
    def __init__(self, headers=None, content_loader=None):
        super().__init__("https://example.com/", headers=headers or {})
        self.id_prefix = "example_"
        self.content_loader = content_loader or RequestContentLoader()

    def get_page_content(self, page_url: str) -> str:
        return self.content_loader.load_content(page_url=page_url)

    def get_pagination_details(self, page_url: str) -> dict:
        return {
            "current_page": 1,
            "total_pages": 1,
            "next_page_url": None,
        }

    def get_product_listings(self, listings_page_url: str, page: int = 1) -> list[str]:
        ...

    def get_product_details(self, product_page_url: str) -> Product:
        ...
```

Required methods:

| Method | Required behavior |
| --- | --- |
| `get_page_content(page_url)` | Load and return page HTML. Raise a scraper exception if loading fails. |
| `get_pagination_details(page_url)` | Return exactly `current_page`, `total_pages`, and `next_page_url`. |
| `get_product_listings(listings_page_url, page=1)` | Return non-empty absolute product URLs with no duplicates. |
| `get_product_details(product_page_url)` | Return a `scraperkit.models.Product` object. |

`get_product_details()` must populate these product fields:

| Field | Requirement |
| --- | --- |
| `id` | Stable source-specific ID, usually prefixed with the source name. |
| `title` | Non-empty product title. |
| `price` | Numeric price as `float`; strip currency symbols and commas before parsing. |
| `description` | Non-empty product description. |
| `url` | Absolute product page URL. |
| `image_url` | Absolute primary product image URL. |
| `page_content` | Product page body used for parsing. It should be present in scraper output, but persistence replaces it with `PAGE_BODY_CONTENT` to avoid storing raw HTML in MongoDB. |

Optional fields should still be returned when available: `category`, `gender`,
`colors`, `sizes`, `material`, `rating`, `review_count`, `scraped_datetime`,
`processed_datetime`, and `page_index`.

Implementation rules:

1. Accept `headers=None` and `content_loader=None` in the constructor so tests can inject static loaders.
2. Use the simplest loader that works for the site. Use Selenium or Playwright only when the page requires browser-rendered content.
3. Parse with structured selectors through BeautifulSoup or browser APIs. Avoid fragile string slicing for page structure.
4. Return absolute URLs from listing and product image extraction.
5. Raise the existing scraper exceptions instead of returning partial invalid data:
   - `ContentNotLoadedException` when the page cannot be loaded.
   - `DataComponentNotFoundException` when a required selector or value is missing.
   - `DataParsingException` when a component exists but cannot be parsed.
6. Do not swallow parser breakage. A failed scraper should fail the job clearly so the source can be fixed.
7. Close loader resources through `close()`; `BaseScraper.close()` already closes `self.content_loader`.

Registration steps for a new scraper:

1. Add the scraper class under `scraperkit/scrapers/`.
2. Export it from `scraperkit/scrapers/__init__.py`.
3. Register it in `scraperkit/__init__.py` inside `SCRAPER_URL_MAP`.
4. Use the domain key returned by `extract_domain(url)`. For example, `https://bluorng.com/...` maps to `bluorng`.
5. Add a live scraper case in `tests/scrapers/cases.py`.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Start a Celery worker for scraping jobs:

```bash
celery -A api.celery_worker.celery_app worker -Q scraping_agent_scrape_medium --loglevel=info --concurrency=5
```

Default local URL: `http://localhost:8080`

## API

Routes are mounted under `/api/scrapingagent/scrape`.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/scrapingagent/scrape/` | Start a scrape job. |
| `GET` | `/api/scrapingagent/scrape/{task_id}/status/` | Fetch job status. |
| `GET` | `/api/scrapingagent/scrape/{task_id}/result/` | Fetch job result. |

## Environment

```bash
MONGO_URI=
MONGO_DBNAME=
API_ACCESS_TOKEN=
REDIS_URL=
PLATFORM=
```

`REDIS_URL` is optional. If it is empty or unset, Celery uses local Redis at
`redis://localhost:6379/0`. For Docker Compose, use `redis://redis:6379/0`.
For Upstash, put the complete `rediss://...` connection URL in `REDIS_URL`.

## Testing

```bash
make test-scraperkit
```

Scraper tests may hit real websites and may require network access plus a valid `PLATFORM` setting for Selenium-based loaders.

## Contribution Scope

External pull requests are accepted only for adding or improving website scrapers.

For scraper PRs:

1. Add or update scraper code under `scraperkit/scrapers/`.
2. Follow the scraper implementation contract above.
3. Register the scraper in `SCRAPER_URL_MAP`.
4. Add or update tests under `tests/scrapers/`.
5. Run `make test-scraperkit` or document why it could not be run.
