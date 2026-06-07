# Project TODO

Unified project-level tracker for Wearlytic. Service-specific TODO files remain
the source of detailed implementation notes:

- [web-app/TODO.md](web-app/TODO.md)
- [backend/TODO.md](backend/TODO.md)
- [data-ingestor/TODO.md](data-ingestor/TODO.md)
- [scraping-agent/TODO.md](scraping-agent/TODO.md)

## Planned Changes

### Data Ingestion Reliability

- [ ] Stagger ingestion schedules into listing scraping, batch creation, then batch processing.
  - Owner: `data-ingestor`
  - Avoid running scheduled listing scraping, batch creation, and batch processing at the same time or too close together.
  - Make the ordered pipeline explicit so each stage is less dependent on the previous task's execution timing.

- [ ] Add stale scraping-agent job timeout handling.
  - Owner: `data-ingestor`
  - Mark stuck `queued` or `processing` scrape statuses as failed after a configurable timeout.

### Scraping Reliability and Extensibility

- [ ] Harden Mongo connectivity and dead job handling for scraping-agent Celery product tasks.
  - Owner: `scraping-agent`
  - Reuse Mongo clients, limit active MongoDB connections per project session, bound connection startup, and persist failed jobs when manager construction fails.

- [ ] Refactor scraper creation to a config-driven factory pattern.
  - Owner: `scraping-agent`
  - Build source scrapers from YAML configs while preserving the current scraper contract during migration.

- [ ] Patch Myntra pagination to parse next-page URLs from the current page.
  - Owner: `scraping-agent`
  - Preserve filter query parameters by extracting the real next page URL instead of building `p=n+1`.

- [ ] Patch BluOrng pagination after the site schema change.
  - Owner: `scraping-agent`
  - Switch BluOrng from the infinity-scroll loader to a simple page loader and follow parsed next-page URLs.

- [ ] Add OffDuty source support.
  - Owner: `scraping-agent`

- [ ] Add Rare Rabbit source support.
  - Owner: `scraping-agent`
