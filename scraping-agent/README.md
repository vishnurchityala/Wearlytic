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
RUN_TYPE_LOCAL=
UPSTASH_REDIS_HOST=
UPSTASH_REDIS_PORT=
UPSTASH_REDIS_PASSWORD=
PLATFORM=
```

## Testing

```bash
make test-scraperkit
```

Scraper tests may hit real websites and may require network access plus a valid `PLATFORM` setting for Selenium-based loaders.

## Contribution Scope

External pull requests are accepted only for adding or improving website scrapers.

For scraper PRs:

1. Add or update scraper code under `scraperkit/scrapers/`.
2. Follow the existing base scraper contracts and product/listing model shapes.
3. Add or update tests under `tests/scrapers/`.
4. Run `make test-scraperkit` or document why it could not be run.
