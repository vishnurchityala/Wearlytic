# TODO

Upcoming development changes for this service should be listed here.

## Planned Changes

- [ ] Harden Mongo connectivity and dead job handling for Celery product tasks.
  - Add a shared Mongo connection helper so `JobsManager` and `JobResultsManager` reuse a cached `MongoClient` per worker process instead of constructing a new client for each task.
  - Make Mongo bootstrap bounded and configurable with `MONGO_SERVER_SELECTION_TIMEOUT_MS` and `MONGO_CONNECT_TIMEOUT_MS`, defaulting to `5000`.
  - Keep collection names configurable with defaults through `JOBS_COLLECTION_NAME` and `JOB_RESULTS_COLLECTION_NAME`.
  - Move manager construction inside the handled task flow or a task wrapper so DNS/client startup failures are caught and recorded as failed jobs when possible, instead of escaping as unexpected Celery exceptions.
  - Keep the public REST API, Celery queue names, and scraper behavior unchanged.
  - Verify with unit tests for Mongo client reuse, manager construction failures, existing failure persistence, and a Docker product batch run that no task stays indefinitely pending after a transient Mongo connection failure.

- [ ] Add OffDuty source support.
- [ ] Add Rare Rabbit source support.
