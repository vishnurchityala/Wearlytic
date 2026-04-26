# BUGS.md

## Scope

This file lists the top high-priority bugs found during a static review of the `data-ingestor` project.

Inclusion bar:

- unauthorized access or privileged action exposure,
- duplicate or incorrect ingestion behavior,
- permanent data loss or state corruption.

Reviewed on: 2026-04-27.

## High-Priority Bugs

### 1. Unauthenticated Celery trigger endpoints allow anonymous job execution

Affected files:

- `app/routes/ingest.py`

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
- This is a direct server-side privilege bypass.
- It can create cost spikes, duplicate workload, and untrusted operator control over ingestion timing.

Fix direction:

- Enforce session/auth checks inside each trigger route.
- Prefer a shared auth dependency instead of per-route copy/paste checks.
- Add CSRF protection for dashboard-originated form posts.

### 2. Admin sessions can be forged because the signing secret is hard-coded

Affected files:

- `main.py`
- `app/routes/security.py`
- `app/routes/dashboard.py`
- `app/routes/source.py`
- `app/routes/listing.py`

What happens:

- Session cookies are signed with hard-coded `SessionMiddleware(secret_key="vrcftw")`.
- Admin access is granted by the presence of `request.session["user"]`.
- If the signing key is known, a client can forge a valid admin session cookie.

Why this is high priority:

- Forged sessions can reach dashboard and source/listing management routes.
- Combined with unauthenticated trigger endpoints, this exposes operational control of the ingestion pipeline.

Fix direction:

- Move the session secret to an environment variable.
- Rotate the secret.
- Invalidate old sessions after rotation.

### 3. Listing scraping is not idempotent and can requeue listings already in progress

Affected files:

- `app/db/listing.py`
- `app/celery_worker.py`
- `app/routes/ingest.py`

What happens:

- `get_oldest_listings_per_source()` selects the oldest active listing per source based only on `last_listed`.
- `start_scraping_listing()` immediately creates a new `Status(status="processing")`, but never checks whether the same listing already has an in-flight processing status.
- `last_listed` is updated only after results are fetched.
- A scheduled run or manual trigger before completion can enqueue the same listing again.

Why this is high priority:

- The same listing can be scraped multiple times concurrently.
- This wastes scraper capacity and can create duplicate downstream `ProductUrl` data.
- It increases race conditions around status updates and ingestion.

Fix direction:

- Exclude listings with in-flight `Status(status="processing")` records.
- Add a first-class listing execution state or idempotency key.
- Make listing dispatch idempotent on `(entity_id, ingestion_type="listing", status="processing")`.
