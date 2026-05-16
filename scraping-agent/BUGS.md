# BUGS.md

## Scope

This file lists the top high-priority bugs found during a static review of the `scraping-agent` project.

Inclusion bar:

- duplicate or incorrect scraping behavior,
- API/job-state reliability issues,
- failures that can block the scraping pipeline or mislead dependent services.

Reviewed on: 2026-04-27.

## High-Priority Bugs

### 1. Scrape job creation is not idempotent

Affected files:

- `api/routes/scrape.py`
- `api/db/job.py`
- `api/celery_worker.py`

What happens:

- Every `POST /api/scrapingagent/scrape/` request creates a new UUID job.
- The route does not check whether the same URL and page type are already queued or processing.
- Repeated client retries or orchestration retries create duplicate scraping work.

Why this is high priority:

- Expensive scraper jobs can run multiple times for the same URL.
- Downstream services can receive duplicate or conflicting results.
- This directly affects ingestion cost and queue load.

Fix direction:

- Add an idempotency key or dedupe on `(webpage_url, type_page, active status)`.
- Return the existing queued/processing job when appropriate.
- Add tests for duplicate request handling.

### 2. MongoDB access has no shared client or explicit server timeout

Affected files:

- `api/db/job.py`
- `api/db/job_results.py`

What happens:

- Each manager creates a new `MongoClient(MONGO_URI)` in `__init__`.
- There is no explicit `serverSelectionTimeoutMS`.
- API routes instantiate managers at module import time.

Why this is high priority:

- MongoDB connectivity issues can hang status/result endpoints longer than expected.
- Repeated manager creation increases connection churn.
- Import-time manager creation makes failures harder to isolate.

Fix direction:

- Use a shared Mongo client helper with explicit timeouts.
- Configure TLS/connection options consistently through environment variables.
- Delay DB access until route/task execution when possible.

### 3. API base endpoint advertises stale routes

Affected files:

- `api/routes/base.py`
- `api/routes/scrape.py`
- `api/routes/status.py`

What happens:

- `GET /api/scrapingagent/` advertises `/api/scrape/...` and `/api/scraper/...`.
- The real route prefix is `/api/scrapingagent/scrape`.
- Dependent services or operators using the base endpoint receive incorrect integration instructions.

Why this is high priority:

- The data-ingestor depends on the scraping-agent contract.
- Stale discovery output increases the chance of broken deployments and incorrect `SCRAPING_AGENT_API_URL` values.

Fix direction:

- Update the base endpoint to reflect real paths.
- Add a simple route contract test for the advertised endpoints.
- Keep README, CONTEXT, and API base output aligned.
