<p align="center">
  <img src="web-app/public/WEARLYTIC-LOGO-2026.png" alt="Wearlytic logo" width="320" />
</p>

# Wearlytic

Wearlytic is a monorepo for fashion product discovery, scraping, ingestion, and AI-assisted outfit generation.

## Services

| Service | Tech | Responsibility | Local README |
| --- | --- | --- | --- |
| `web-app/` | ![React](https://img.shields.io/badge/React-20232a?logo=react&logoColor=61dafb) ![Vite](https://img.shields.io/badge/Vite-646cff?logo=vite&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind-06b6d4?logo=tailwindcss&logoColor=white) | React + Vite web app for authentication, product browsing, user profile management, and image-generation workflows. | [web-app/README.md](web-app/README.md) |
| `backend/` | ![Django](https://img.shields.io/badge/Django-092e20?logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-a30000) ![Supabase](https://img.shields.io/badge/Supabase-3fcf8e?logo=supabase&logoColor=white) | Django REST API for users, products, categories, Supabase JWT authentication, storage integration, and image generation. | [backend/README.md](backend/README.md) |
| `scraping-agent/` | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Celery](https://img.shields.io/badge/Celery-37814a) ![Selenium](https://img.shields.io/badge/Selenium-43b02a?logo=selenium&logoColor=white) | FastAPI + Celery service that runs website-specific product and listing scrapers. | [scraping-agent/README.md](scraping-agent/README.md) |
| `data-ingestor/` | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47a248?logo=mongodb&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-dc382d?logo=redis&logoColor=white) | FastAPI + Celery orchestration service for sources, listings, scrape batches, job status, and product warehouse ingestion. | [data-ingestor/README.md](data-ingestor/README.md) |

## Contribution Policy

This project currently accepts external pull requests only for adding or improving website scrapers in `scraping-agent/`.

Before opening a scraper PR:

1. Add the scraper implementation under `scraping-agent/scraperkit/scrapers/`.
2. Follow the existing scraper contracts and model shapes.
3. Add or update scraper tests under `scraping-agent/tests/`.
4. Run the relevant scraping-agent checks documented in [scraping-agent/README.md](scraping-agent/README.md).

Pull requests for `web-app/`, `backend/`, or `data-ingestor/` are not accepted unless maintainers explicitly request them.

## License

Wearlytic is released under the [Apache License 2.0](LICENSE).
