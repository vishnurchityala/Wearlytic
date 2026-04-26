# BUGS.md

## Scope

This file lists the high-priority bugs found during a static review of the `data-ingestor` project folder.

Inclusion bar:

- unauthorized access or privileged action exposure,
- duplicate or incorrect ingestion behavior,
- permanent data loss / state corruption,
- broken local startup path that the repo itself documents as supported.

Line numbers refer to the current working tree as reviewed on `2026-04-18`.

## High-Priority Bugs

### 1. Unauthenticated Celery trigger endpoints allow anonymous job execution

Affected files:

- `app/routes/ingest.py:7-24`

What happens:

- All four side-effecting trigger routes call `.delay()` directly.
- None of them check `request.session`, admin identity, or any other auth gate.
- A client can POST to:
  - `/api/trigger-batch-scrape`
  - `/api/trigger-batch-create`
  - `/api/trigger-status-update`
  - `/api/trigger-listing-scrape`
  without logging in.

Why this is high priority:

- Any unauthenticated caller can enqueue scraping work, poll jobs, and drive background load.
- This is a direct server-side privilege bypass, not just a UI issue.
- It can create cost spikes, duplicate workload, and untrusted operator control over ingestion timing.

Fix direction:

- Enforce session/auth checks inside each trigger route.
- Prefer shared auth dependency/middleware instead of per-route copy/paste checks.
- Add CSRF protection for dashboard-originated form posts.

### 2. Admin sessions can be forged because the signing secret is hard-coded, and repository secrets are committed

Affected files:

- `main.py:8-10`
- `app/routes/security.py:60-61`
- `.env:1-23`
- `app/routes/dashboard.py:29-86`
- `app/routes/source.py:42-47`
- `app/routes/listing.py:37-45`

What happens:

- Session cookies are signed with a hard-coded `SessionMiddleware` secret in source.
- Admin access is granted purely by the presence of `request.session["user"]`.
- The repository also contains a checked-in `.env` with live-looking credentials/tokens instead of a template-only file.

Why this is high priority:

- Anyone who knows the session secret can forge a valid admin cookie and reach the dashboard plus source/listing management routes.
- Committed secrets also expose the admin login, scraping token, database access, and broker credentials to anyone with repo access.
- Together, this is effectively full admin compromise.

Fix direction:

- Move the session secret to environment configuration and rotate it.
- Remove committed secrets from the repo and replace `.env` with `.env.example`.
- Invalidate existing sessions after rotation.

### 3. Listing scraping is not idempotent and will requeue listings that are already in progress

Affected files:

- `app/db/listing.py:95-113`
- `app/celery_worker.py:111-136`
- `app/celery_worker.py:289-312`
- `app/celery_worker.py:392-401`
- `app/routes/ingest.py:22-24`

What happens:

- `get_oldest_listings_per_source()` selects the oldest active listing per source based only on `last_listed`.
- `start_scraping_listing()` immediately creates a new `Status(status="processing")` for that listing, but it never checks whether the same listing already has a processing record.
- `last_listed` is only updated when results are ingested later in `fetch_results()`.
- A manual retrigger or another scheduled run before completion picks the same listing again and creates another scrape job.

Why this is high priority:

- The same listing can be scraped multiple times concurrently.
- This wastes scraping capacity, produces duplicate status rows, and increases race conditions around downstream `ProductUrl` creation.
- Because the queue is operator-triggerable, this is easy to reproduce accidentally.

Fix direction:

- Exclude listings that already have an in-flight `Status` record.
- Consider a first-class listing state such as `idle / queued / processing`.
- Make listing dispatch idempotent on `(entity_id, status='processing')`.

### 4. Batch/product scraping is not idempotent and can requeue the same product URLs before prior runs finish

Affected files:

- `app/db/batch.py:174-206`
- `app/celery_worker.py:202-255`
- `app/celery_worker.py:263-385`
- `app/celery_worker.py:415-429`
- `app/routes/ingest.py:7-10`

What happens:

- `scrape_batch()` selects batches from `get_top_n_batches()` with no check for in-flight product statuses.
- For each `product_url_id`, it creates a new product scrape job and a new `processing` status row.
- The batch is marked `last_processed` immediately after dispatch, not after result ingestion.
- If the route is manually triggered again, or if scheduled reruns happen while results are still pending, the same batch can be selected again and the same product URLs are resubmitted.

Why this is high priority:

- The service can launch duplicate product scrapes for the same URLs.
- That drives redundant external work and creates conflicting product updates/status rows.
- This is especially damaging because product scraping is the expensive stage and the worker is configured as a single-threaded bottleneck.

Fix direction:

- Track batch execution state separately from `last_processed`.
- Skip batches or product URLs that already have `processing` statuses.
- Only advance the batch to a completed timestamp once all product results have been resolved.

### 5. Scraping Agent failures are handled as permanent job failures, and several critical HTTP calls have no timeout

Affected files:

- `app/celery_worker.py:124`
- `app/celery_worker.py:274-285`
- `app/celery_worker.py:376-385`
- `app/celery_worker.py:226-230`

What happens:

- `start_scraping_listing()` posts to the Scraping Agent without a timeout.
- `fetch_results()` calls both status and result endpoints without a timeout.
- `fetch_results()` also calls `.json()` immediately without checking HTTP status codes first.
- Any transient network error, non-JSON error body, or temporary Scraping Agent 5xx causes the status row to be flipped to `failed`.

Why this is high priority:

- A temporary dependency glitch becomes a permanent lost job in this system.
- Because `fetch_results()` stops polling once a row is marked failed, data can be silently dropped even if the external job completes later.
- Missing timeouts can hang the single Celery worker indefinitely, blocking the whole pipeline.

Fix direction:

- Set explicit timeouts on all Scraping Agent HTTP calls.
- Check `response.status_code` before parsing JSON.
- Distinguish transport/parsing errors from actual scrape job failure; retry transient errors instead of permanently failing the status row.

### 6. Deleting a source or listing leaves dependent collections orphaned and can break later ingestion runs

Affected files:

- `app/routes/source.py:107-110`
- `app/routes/listing.py:79-82`
- `app/celery_worker.py:214-218`
- `app/celery_worker.py:286-287`
- `app/celery_worker.py:340-346`

What happens:

- Deleting a source only deletes its listing documents.
- Deleting a listing only removes the listing itself and its source reference.
- Neither path cleans up related `ProductUrl`, `Status`, `Batch`, or `Product` documents.
- Later pipeline stages assume those linked documents still resolve cleanly.

Why this is high priority:

- The warehouse can enter an inconsistent state with orphaned product URLs, stale statuses, and batches referencing deleted upstream records.
- Future `scrape_batch()` runs can hit missing `ProductUrl` documents.
- Future `fetch_results()` runs can fail when they resolve deleted listings or product URLs, turning real scrape results into failed ingestion.

Fix direction:

- Define explicit cascade behavior for all dependent collections.
- Either hard-delete the whole dependency chain or soft-delete and exclude deleted entities from the pipeline.
- Add referential cleanup to source/listing deletion paths before exposing delete actions in production.

### 7. The documented local MongoDB startup path is broken because the client always forces TLS

Affected files:

- `app/utils/__init__.py:18-22`
- `Makefile:16`
- `Makefile:78-81`
- `.env:11-12`

What happens:

- `get_client()` always creates `MongoClient(..., tls=True, tlsCAFile=...)`.
- The repo also documents a local startup path via `make run` and a commented local `mongodb://localhost:27017/` URI in `.env`.
- Standard local `mongodb-community` installs started by Homebrew do not use TLS by default.

Why this is high priority:

- The repo advertises local Mongo support, but the current client configuration prevents that path from working in the normal local setup.
- This blocks local development, debugging, and recovery work when Atlas access is unavailable.

Fix direction:

- Make TLS configurable instead of unconditional.
- Derive client options from the URI scheme or dedicated env flags.
- Keep the Makefile, `.env.example`, and Mongo client behavior consistent.

## Not Included

The following issues were observed but are not listed as high priority here:

- partial `Product` refresh behavior when a product already exists,
- `BatchManager` sorting by `created_at` even though the model does not define it,
- the dashboard edit-listing modal JavaScript reference error,
- denormalized counter drift risk in `$addToSet` + `$inc` update patterns.

Those should still be addressed, but they are lower priority than the seven issues above.
