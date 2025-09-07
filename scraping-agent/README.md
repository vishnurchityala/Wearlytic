
# Scraping Agent

This folder contains a modular web scraping service for product and listing data, built with FastAPI, Celery, and custom scrapers.

## Main Components

- **main.py**: FastAPI app entry point.
- **api/**: API endpoints, models, and database logic.
  - `routes/`: Listing, product, and status endpoints.
  - `models/`: Data models for jobs, products, and listings.
- **celery_worker/**: Celery background task definitions.
- **scraperkit/**: Modular scraping framework (base classes, scrapers, loaders, exceptions, etc.).
- **requirements.txt**: Python dependencies.
- **Dockerfile**: Container setup for deployment.
- **Makefile**: Commands to run, stop, and manage the service.

## How It Works

1. Start the FastAPI server (`main.py`).
2. Start Celery workers for background scraping jobs.
3. Use API endpoints to start scraping jobs, check status, and get results.
4. Scrapers in `scraperkit/scrapers/` handle different websites.

## API Endpoints (see `api/routes/`)

- **POST `/api/scrape/listing/`**: Start a listing scrape job
- **GET `/api/scrape/listing/{task_id}/status/`**: Get status of a listing job
- **GET `/api/scrape/listing/{task_id}/result/`**: Get results of a listing job
- **POST `/api/scrape/product/`**: Start a product scrape job
- **GET `/api/scrape/product/{task_id}/status/`**: Get status of a product job
- **GET `/api/scrape/product/{task_id}/result/`**: Get results of a product job

## Extending

- Add new scrapers in `scraperkit/scrapers/`
- Add new API routes in `api/routes/`
- Update models in `api/models/`

## Quick Start

```bash
uvicorn main:app --reload
celery -A celery_worker worker --loglevel=info -Q scrape_medium
```

## License

See [LICENSE](../LICENSE)
