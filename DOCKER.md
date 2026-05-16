# Docker Local Development

This compose setup runs the four active Wearlytic services:

- `web-app` on `http://localhost:5173`
- `backend` on `http://localhost:8000`
- `scraping-agent` on `http://localhost:8080`
- `data-ingestor` on `http://localhost:8081`

Cloud-managed databases stay outside Docker. Runtime secrets and database URLs come
from each service's existing `.env` file through Compose `env_file`.

## Start The Stack

```bash
docker compose build
docker compose up
```

Run in the background:

```bash
docker compose up -d
```

Stop everything:

```bash
docker compose down
```

## Service Notes

- `web-app` runs the Vite dev server and overrides `VITE_API_BASE_URL` to
  `http://localhost:8000/api` so browser requests hit the local Django backend.
- `backend` runs Django's development server and uses cloud Supabase/Postgres
  settings from `backend/.env`.
- `scraping-agent` runs Redis, three Celery workers, and Uvicorn in one
  container. Its Celery broker is `redis://127.0.0.1:6379/0` inside that
  container. Compose runs this service as `linux/amd64` so Selenium uses the
  bundled `scraperkit/drivers/chromedriver-linux64/chromedriver`.
- `data-ingestor` runs Redis, one Celery worker, Celery beat, and Uvicorn in one
  container. It calls the scraping agent through Docker DNS at
  `http://scraping-agent:8080/api/scrapingagent`.

## Scraping Browser

The local-dev scraping image does not install Chrome, Chromium, or GUI browser
packages. Before using Selenium-backed scrapers through Docker, start headless
Chrome on the Mac host with remote debugging enabled:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --remote-debugging-address=0.0.0.0 \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/wearlytic-chrome \
  --no-first-run \
  --no-default-browser-check
```

Compose sets `SELENIUM_REMOTE_DEBUGGER_ADDRESS=host.docker.internal:9222`, so
ChromeDriver inside the scraping container attaches to that host browser. This
keeps the image small and avoids the slow Chromium download during
`docker compose build`.

## Future Nginx Gateway

The current setup is local-dev first and exposes each service directly. A future
production-style setup can add an Nginx service that routes `/api/` to
`backend`, frontend traffic to the built web app, and internal admin/scraping
routes to the relevant FastAPI services.
