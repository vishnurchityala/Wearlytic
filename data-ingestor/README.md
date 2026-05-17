# Data Ingestor

![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814a)
![Redis](https://img.shields.io/badge/Redis-dc382d?logo=redis&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47a248?logo=mongodb&logoColor=white)

The data ingestor orchestrates Wearlytic's scraping and product warehouse pipeline.

## Responsibility

- Manage source and listing definitions.
- Trigger listing and product scrape jobs through the scraping agent.
- Track asynchronous scrape job statuses.
- Create product URL batches for downstream product-page scraping.
- Store ingested product records in MongoDB.
- Serve the internal admin dashboard for ingestion operations.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8081
```

Start worker and scheduler processes when running the full pipeline:

```bash
celery -A app.celery_worker worker -Q data_ingestor_queue -P solo -c 1 --loglevel=info
celery -A app.celery_worker beat --loglevel=info
```

Default local URL: `http://localhost:8081`

## Make Targets

```bash
make run
make stop
make test-scraping-agent
```

## Environment

```bash
SCRAPING_AGENT_API_URL=
SCRAPING_AGENT_TOKEN=
MONGO_URI=
MONGO_DBNAME=
ADMIN_USERNAME=
ADMIN_PASSWORD=
MAXIMUM_BATCH_SIZE=
MAXIMUM_BATCHES_TO_PROCESS=
REDIS_URL=
```

`REDIS_URL` is optional. If it is empty or unset, Celery uses local Redis at
`redis://localhost:6379/0`. For Docker Compose, use `redis://redis:6379/0`.
For Upstash, put the complete `rediss://...` connection URL in `REDIS_URL`.

The DB modules also use collection-name environment variables for sources, listings, batches, statuses, product URLs, and products.

## Page Content Storage

New product writes store `PAGE_BODY_CONTENT` in `page_content` instead of raw
HTML to keep MongoDB documents small. Existing documents can be cleaned with a
one-time MongoDB update:

```bash
mongosh "$MONGO_URI" --eval '
const database = process.env.MONGO_DBNAME;
const products = process.env.PRODUCTS_COLLECTION_NAME || "data_ingestor_products";
const target = db.getSiblingDB(database);
target.scraping_agent_job_results.updateMany(
  {"result.page_content": {$exists: true}},
  {$set: {"result.page_content": "PAGE_BODY_CONTENT"}}
);
target[products].updateMany(
  {page_content: {$exists: true}},
  {$set: {page_content: "PAGE_BODY_CONTENT"}}
);
'
```

## Contribution Scope

External pull requests are not currently accepted for this service unless maintainers explicitly request them. Wearlytic currently accepts external PRs only for adding or improving website scrapers in [`../scraping-agent`](../scraping-agent/README.md).
