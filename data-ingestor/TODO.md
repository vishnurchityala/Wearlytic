# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Add stale scraping-agent job timeout handling.
  - Store `created_at` on new scraping-agent status records and add `SCRAPING_AGENT_JOB_TIMEOUT_SECONDS`, defaulting to `3600`.
  - Update `fetch_results()` to mark `queued` or `processing` jobs as `failed` when they exceed the timeout, so a scraping-agent Celery/DNS failure cannot leave ingestion batches stuck forever.
  - Cover fresh versus stale `queued` and `processing` statuses with tests.

- [ ] Fix batch internal fragmentation when adding URLs to previously processed batches.
  - When a new `ProductUrl` is appended to a batch that already has `last_processed` set, the batch can be skipped by processing order because it looks recently handled.
  - Ensure adding new URLs makes the batch eligible for product scraping again, or avoid reusing processed batches for unprocessed URLs.
  - Cover the case where an old processed batch receives a new URL and that URL is scraped on the next batch-processing pass.
