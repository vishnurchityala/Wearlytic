# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Harden Mongo connectivity and dead job handling for Celery product tasks.
  - Add a shared Mongo connection helper so `JobsManager` and `JobResultsManager` reuse a cached `MongoClient` per worker process instead of constructing a new client for each task.
  - Limit active MongoDB connections per project session with explicit pool settings such as `MONGO_MAX_POOL_SIZE`, `MONGO_MIN_POOL_SIZE`, and `MONGO_MAX_IDLE_TIME_MS`.
  - Make the pool limit low enough for the current Celery worker model so concurrent scraper tasks do not exhaust the MongoDB project connection cap.
  - Make Mongo bootstrap bounded and configurable with `MONGO_SERVER_SELECTION_TIMEOUT_MS` and `MONGO_CONNECT_TIMEOUT_MS`, defaulting to `5000`.
  - Keep collection names configurable with defaults through `JOBS_COLLECTION_NAME` and `JOB_RESULTS_COLLECTION_NAME`.
  - Move manager construction inside the handled task flow or a task wrapper so DNS/client startup failures are caught and recorded as failed jobs when possible, instead of escaping as unexpected Celery exceptions.
  - Keep the public REST API, Celery queue names, and scraper behavior unchanged.
  - Verify with unit tests for Mongo client reuse, connection-pool option wiring, manager construction failures, existing failure persistence, and a Docker product batch run that no task stays indefinitely pending after a transient Mongo connection failure.

- [ ] Add Rare Rabbit source support.

- [ ] Refactor scraper creation to a config-driven factory pattern.
  - Replace one specialized scraper class per source with a scraper factory that builds scrapers from source config.
  - Store each source config in YAML files so selectors, loaders, pagination rules, and extraction rules can be changed without adding a new scraper class.
  - Preserve existing scraper contracts, `SCRAPER_URL_MAP` behavior, and tests while migrating sources incrementally.

- [ ] Patch Myntra pagination to parse next-page URLs from the current page.
  - Stop building the next page with static `p=n+1` query parameter typing.
  - Parse the current listing page and extract the real next page URL so filtered Myntra URLs keep their filter query parameters.
  - Add a regression test for filtered Myntra listing URLs.

- [ ] Patch BluOrng pagination and switch away from the infinity-scroll loader.
  - BluOrng changed its listing pagination schema, so the current `SeleniumInfinityScrollContentLoader` flow no longer matches the site behavior.
  - Use a simple page loader for BluOrng listing pages and parse the real next-page URL from the current page.
  - Update `BluOrngScraper.get_pagination_details()` so listing scraping advances by `next_page_url` instead of assuming a single infinite-scroll page.
  - Add regression coverage for BluOrng listing pagination, including the final page with no next-page URL.
