# Wearlytic Context

This file gives repository-level context for agents and contributors working in the Wearlytic monorepo.

## Project Scope

Wearlytic is a fashion-tech monorepo for product discovery, website scraping, product ingestion, and AI-assisted outfit generation.

The active project folders are:

| Folder | Role |
| --- | --- |
| `web-app/` | User-facing React/Vite app for auth, product browsing, profiles, and image-generation workflows. |
| `backend/` | Django REST API for users, products, categories, Supabase auth/storage, and Gemini image generation. |
| `scraping-agent/` | FastAPI + Celery service that runs website-specific listing and product scrapers. |
| `data-ingestor/` | FastAPI + Celery orchestration service for sources, listings, batches, scrape status, and product warehouse ingestion. |

Older or supporting folders may exist, but the root README intentionally points contributors to the four active services above.

## Runtime Flow

1. `web-app` authenticates users with Supabase and calls the Django backend.
2. `backend` serves product/category/user APIs and image-generation endpoints.
3. `data-ingestor` manages source/listing metadata and schedules scraping work.
4. `scraping-agent` performs the actual website scraping and stores job status/results.
5. `data-ingestor` polls scrape results and writes product warehouse records.

## Service Context Files

Read the local context file before changing a service:

- `web-app/CONTEXT.md`
- `backend/CONTEXT.md`
- `scraping-agent/CONTEXT.md`
- `data-ingestor/CONTEXT.md`

## Contribution Policy

External pull requests are currently accepted only for adding or improving website scrapers in `scraping-agent/`.

Do not open unsolicited PRs for `web-app`, `backend`, or `data-ingestor` unless maintainers explicitly request them.

## Secrets

Do not commit `.env` files, service-role keys, database URLs, OAuth secrets, API tokens, or generated local runtime state.

## Generated Files

Avoid committing local runtime output such as:

- `node_modules/`
- `dist/`
- Python virtual environments
- `__pycache__/`
- `.pytest_cache/`
- Celery Beat schedule databases
- local SQLite databases unless intentionally part of a fixture

## Documentation

- Root `README.md` should stay short and service-focused.
- Each service owns its own README, TODO, and CONTEXT files.
- Put upcoming service work in that service's `TODO.md`.
