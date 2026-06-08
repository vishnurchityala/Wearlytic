# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Add stale scraping-agent job timeout handling.
  - Store `created_at` on new scraping-agent status records and add `SCRAPING_AGENT_JOB_TIMEOUT_SECONDS`, defaulting to `3600`.
  - Update `fetch_results()` to mark `queued` or `processing` jobs as `failed` when they exceed the timeout, so a scraping-agent Celery/DNS failure cannot leave ingestion batches stuck forever.
  - Cover fresh versus stale `queued` and `processing` statuses with tests.
