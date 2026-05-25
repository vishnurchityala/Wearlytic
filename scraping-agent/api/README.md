# Scraping Agent API

FastAPI API package for the Wearlytic scraping agent.

## How It Works

- Starts scraping jobs for product listings or individual products.
- Checks asynchronous job status.
- Returns completed scrape results.
- Uses Celery for background task execution.

## API Endpoints

Routes are mounted under `/api/scrapingagent/scrape`.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/scrapingagent/scrape/` | Start a scrape job. |
| `GET` | `/api/scrapingagent/scrape/{task_id}/status/` | Get scrape job status. |
| `GET` | `/api/scrapingagent/scrape/{task_id}/result/` | Get completed scrape results. |

## Deployment

The root [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml)
workflow deploys this API as part of the `scraping-agent` service. On every push
to `main`, it rebuilds `scraping-agent` and `data-ingestor` on the VPS with:

```bash
docker compose up -d scraping-agent data-ingestor --build --remove-orphans
```

## Extending

- Add scrapers in `scraperkit/scrapers/`
- Add routes in `api/routes/`
- Update models in `api/models/`
