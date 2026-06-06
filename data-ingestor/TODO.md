# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Stagger ingestion schedules so the pipeline runs listing scraping -> batch creation -> batch processing.
  - Current scheduled jobs can run too close together, which makes batch creation and batch processing depend on whether the previous task finished in time.
  - Keep `start_scraping_listing`, `create_product_batches`, and `scrape_batch` on separate windows with enough delay for listing result polling and product URL creation.
  - Preserve `fetch_results()` as the frequent polling task, but make the daily pipeline order explicit in `app/celery_worker.py`.
  - Document the chosen schedule in `data-ingestor/README.md` and `data-ingestor/CONTEXT.md`.

- [ ] Add stale scraping-agent job timeout handling.
  - Store `created_at` on new scraping-agent status records and add `SCRAPING_AGENT_JOB_TIMEOUT_SECONDS`, defaulting to `3600`.
  - Update `fetch_results()` to mark `queued` or `processing` jobs as `failed` when they exceed the timeout, so a scraping-agent Celery/DNS failure cannot leave ingestion batches stuck forever.
  - Cover fresh versus stale `queued` and `processing` statuses with tests.

- [ ] Fix batch internal fragmentation when adding URLs to previously processed batches.
  - When a new `ProductUrl` is appended to a batch that already has `last_processed` set, the batch can be skipped by processing order because it looks recently handled.
  - Ensure adding new URLs makes the batch eligible for product scraping again, or avoid reusing processed batches for unprocessed URLs.
  - Cover the case where an old processed batch receives a new URL and that URL is scraped on the next batch-processing pass.
