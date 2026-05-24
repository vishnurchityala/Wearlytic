# Project TODO

Unified project-level tracker for Wearlytic. Service-specific TODO files remain
the source of detailed implementation notes:

- [web-app/TODO.md](web-app/TODO.md)
- [backend/TODO.md](backend/TODO.md)
- [data-ingestor/TODO.md](data-ingestor/TODO.md)
- [scraping-agent/TODO.md](scraping-agent/TODO.md)

## Planned Changes

### Catalog Stats and Freshness

- [ ] Add backend catalog metadata support for product stats.
  - Owner: `backend`
  - Add `CatalogMetadata` rows for `total_products` and `last_fetched`.
  - Expose a normalized API response with `product_count` and `last_data_fetched`.

- [ ] Show catalog stats and freshness badges in the web app.
  - Owner: `web-app`
  - Display product count on the landing page and playground page.
  - Show a "Last data fetched" badge from backend catalog metadata.

### Data Ingestion Reliability

- [ ] Add stale scraping-agent job timeout handling.
  - Owner: `data-ingestor`
  - Mark stuck `queued` or `processing` scrape statuses as failed after a configurable timeout.

- [ ] Fix batch internal fragmentation for reused product URL batches.
  - Owner: `data-ingestor`
  - Ensure new URLs added to previously processed batches are scraped on the next batch-processing pass.

### Scraping Reliability and Extensibility

- [ ] Harden Mongo connectivity and dead job handling for scraping-agent Celery product tasks.
  - Owner: `scraping-agent`
  - Reuse Mongo clients, bound connection startup, and persist failed jobs when manager construction fails.

- [ ] Refactor scraper creation to a config-driven factory pattern.
  - Owner: `scraping-agent`
  - Build source scrapers from YAML configs while preserving the current scraper contract during migration.

- [ ] Patch Myntra pagination to parse next-page URLs from the current page.
  - Owner: `scraping-agent`
  - Preserve filter query parameters by extracting the real next page URL instead of building `p=n+1`.

- [ ] Add OffDuty source support.
  - Owner: `scraping-agent`

- [ ] Add Rare Rabbit source support.
  - Owner: `scraping-agent`
