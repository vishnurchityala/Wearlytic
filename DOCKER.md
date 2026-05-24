# Docker Local Development

This compose setup runs the four active Wearlytic services:

- `web-app` on `http://localhost:5173`
- `backend` on `http://localhost:8000`
- `scraping-agent` on `http://localhost:8080`
- `data-ingestor` on `http://localhost:8081`

Cloud-managed databases stay outside Docker. Runtime secrets and database URLs come
from each service's existing `.env` file through Compose `env_file`.
The data-ingestor also receives `backend/.env` so it can use the backend
PostgreSQL `DATABASE_URL` for product writes.

## Start The Stack

First build the service images:

```bash
docker compose build
```

Then start the stack:

```bash
docker compose up
```

Run in the background:

```bash
docker compose up -d
```

Stop everything:

```bash
docker compose down --remove-orphans
```

Use `down`, not `stop`, for normal shutdown. `docker compose stop` leaves
containers behind, and those stopped containers can keep old image IDs alive
after rebuilds.

## Rebuild Workflow

For normal daily start/stop without rebuilding images:

```bash
docker compose up -d
docker compose down --remove-orphans
```

When Dockerfiles or dependencies changed, rebuild cleanly:

```bash
docker compose down --remove-orphans --rmi local
docker compose up -d --build
```

If `<none>:<none>` images appear after repeated builds, remove unused dangling
images after the rebuild:

```bash
docker image prune -f
docker builder prune -f
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
- The scraping-agent image installs Chromium and the Linux shared libraries
  needed by the bundled ChromeDriver. It does not install a separate
  ChromeDriver package.
- `data-ingestor` runs Redis, one Celery worker, Celery beat, and Uvicorn in one
  container. It calls the scraping agent through Docker DNS at
  `http://scraping-agent:8080/api/scrapingagent`. MongoDB still stores
  ingestion workflow state, but completed product records are written to the
  backend PostgreSQL `api_category` and `api_product` tables through
  `DATABASE_URL`.
- `backend` and `web-app` do not run local Redis.

## Local Redis Model

Redis is intentionally embedded inside the containers that need it:

- `scraping-agent` starts its own Redis server on `127.0.0.1:6379`.
- `data-ingestor` starts its own Redis server on `127.0.0.1:6379`.

Those Redis servers are isolated inside their containers. They are not shared
with each other and are not exposed as separate Compose services.

Compose sets `REDIS_URL=redis://127.0.0.1:6379/0` for both services so their
Celery workers connect to the Redis instance running in the same container.

## Scraping Browser

The local-dev scraping image installs Chromium inside the container and runs it
headlessly through Selenium. No host Chrome or remote debugging setup is needed.

Important browser settings:

- `platform: linux/amd64` makes the container match the bundled Linux
  ChromeDriver.
- `PLATFORM=linux64` makes scraperkit select
  `scraperkit/drivers/chromedriver-linux64/chromedriver`.
- `CHROME_BIN=/usr/bin/chromium` tells Selenium where the browser binary lives.
- `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium` points Playwright
  loaders at the same Chromium binary.

If Selenium reports `cannot find Chrome binary`, the running container is stale
or was built before Chromium was added. Rebuild only that service:

```bash
docker compose down --remove-orphans
docker compose build scraping-agent
docker compose up -d scraping-agent data-ingestor
```

Verify the browser inside the container:

```bash
docker compose exec scraping-agent sh -lc 'echo "$CHROME_BIN" && which chromium && chromium --version'
```

## Future Nginx Gateway

The current setup is local-dev first and exposes each service directly. A future
production-style setup can add an Nginx service that routes `/api/` to
`backend`, frontend traffic to the built web app, and internal admin/scraping
routes to the relevant FastAPI services.
