<p align="center">
  <img src="web-app/public/WEARLYTIC-LOGO-2026.png" alt="Wearlytic Logo" width="280" />
</p>

<p align="center">
  <img alt="Active" src="https://img.shields.io/badge/status-active-22c55e?logo=checkmarx&logoColor=white" />
  <img alt="Commits" src="https://img.shields.io/github/commit-activity/m/vishnurchityala/Wearlytic?label=commits&color=6366f1&logo=github&logoColor=white" />
  <img alt="License" src="https://img.shields.io/github/license/vishnurchityala/Wearlytic?label=license&color=0ea5e9&logo=apache&logoColor=white" />
</p>

<p align="center">
  An AI-powered fashion intelligence platform for product discovery, data ingestion, trend analysis, and personalized outfit generation.
</p>

## Quick Start

```bash
git clone https://github.com/vishnurchityala/Wearlytic.git
cd Wearlytic
docker compose up -d --build
```

For Docker shutdown, rebuild, and cleanup workflows, see [DOCKER.md](DOCKER.md).

## Services

| Service | Tech | Responsibility | Local README |
| --- | --- | --- | --- |
| `web-app/` | ![React](https://img.shields.io/badge/React-20232a?logo=react&logoColor=61dafb) ![Vite](https://img.shields.io/badge/Vite-646cff?logo=vite&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind-06b6d4?logo=tailwindcss&logoColor=white) | React + Vite web app for authentication, product browsing, user profile management, and image-generation workflows. | [web-app/README.md](web-app/README.md) |
| `backend/` | ![Django](https://img.shields.io/badge/Django-092e20?logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-a30000) ![Supabase](https://img.shields.io/badge/Supabase-3fcf8e?logo=supabase&logoColor=white) | Django REST API for users, products, categories, Supabase JWT authentication, storage integration, and image generation. | [backend/README.md](backend/README.md) |
| `scraping-agent/` | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Celery](https://img.shields.io/badge/Celery-37814a) ![Selenium](https://img.shields.io/badge/Selenium-43b02a?logo=selenium&logoColor=white) | FastAPI + Celery service that runs website-specific product and listing scrapers. | [scraping-agent/README.md](scraping-agent/README.md) |
| `data-ingestor/` | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47a248?logo=mongodb&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-dc382d?logo=redis&logoColor=white) | FastAPI + Celery orchestration service for sources, listings, scrape batches, job status, and product warehouse ingestion. | [data-ingestor/README.md](data-ingestor/README.md) |

## Contribution Policy

This project currently accepts external pull requests only for adding or improving website scrapers in `scraping-agent/`.

Scraper implementations must follow the detailed contract in
[scraping-agent/README.md](scraping-agent/README.md#scraper-implementation-contract).
At a minimum, a scraper should look like this:

```python
from scraperkit.base import BaseScraper
from scraperkit.models import Product


class ExampleScraper(BaseScraper):
    def __init__(self, headers=None, content_loader=None):
        super().__init__("https://example.com/", headers=headers or {})
        self.content_loader = content_loader

    def get_page_content(self, page_url: str) -> str:
        ...

    def get_pagination_details(self, page_url: str) -> dict:
        return {"current_page": 1, "total_pages": 1, "next_page_url": None}

    def get_product_listings(self, listings_page_url: str, page: int = 1) -> list[str]:
        return ["https://example.com/products/example-product"]

    def get_product_details(self, product_page_url: str) -> Product:
        ...
```

Then export it, register it in `SCRAPER_URL_MAP`, and add/update scraper tests
under `scraping-agent/tests/scrapers/`.

Before opening a scraper PR:

1. Add the scraper implementation under `scraping-agent/scraperkit/scrapers/`.
2. Export and register it in the scraping-agent scraper map.
3. Follow the scraper implementation contract linked above.
4. Add or update scraper tests under `scraping-agent/tests/scrapers/`.
5. Run the relevant scraping-agent checks documented in [scraping-agent/README.md](scraping-agent/README.md).

Pull requests for `web-app/`, `backend/`, or `data-ingestor/` are not accepted unless maintainers explicitly request them.

## Commit Messages

Use this format:

```bash
git commit -m "<annotation>: <short descriptive title>" -m "<brief description of what changed and why>"
```

Allowed annotations: `feat`, `fix`, `refactor`, `docs`, `test`, `build`, `ci`, `config`, `deps`, `chore`, `style`, `perf`, `api`, `db`, `queue`, `auth`, `ui`, `security`, `revert`.

## License

Wearlytic is released under the [Apache License 2.0](LICENSE).
