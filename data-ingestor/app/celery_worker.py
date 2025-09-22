"""
Importing Modules for Celery Workers.
"""
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from app.db import ListingsManager, StatusManager, SourceManager, ProductUrlManager, BatchManager, ProductManager
from app.models import Status, ProductUrl, Batch, Product
from dotenv import load_dotenv
import requests
from datetime import datetime, timezone
import uuid
import time
import os

load_dotenv()

"""
Creating Logger fot the Tasks.
"""
logger = get_task_logger(__name__)

listing_manager = ListingsManager()
status_manager = StatusManager()
source_manager = SourceManager()
product_url_manager = ProductUrlManager()
batch_manager = BatchManager()
product_manager = ProductManager()
"""
Celery Queue Configuration.
"""
UPSTASH_REDIS_HOST = os.getenv("UPSTASH_REDIS_HOST")
UPSTASH_REDIS_PORT = os.getenv("UPSTASH_REDIS_PORT")
UPSTASH_REDIS_PASSWORD = os.getenv("UPSTASH_REDIS_PASSWORD")
RUN_TYPE_LOCAL = os.getenv("RUN_TYPE_LOCAL")
if RUN_TYPE_LOCAL == 'YES':
    connection_link ="redis://localhost:6379/0"
else:
    connection_link = f"rediss://:{UPSTASH_REDIS_PASSWORD}@{UPSTASH_REDIS_HOST}:{UPSTASH_REDIS_PORT}?ssl_cert_reqs=none"
app = Celery(
    "dataingestor",
    broker=connection_link,
    backend = 'rpc://'
)

SCRAPING_AGENT_ENDPOINT = os.getenv("SCRAPING_AGENT_API_URL")
SCRAPING_AGENT_TOKEN = os.getenv("SCRAPING_AGENT_TOKEN")
headers = {
    "Authorization": f"Bearer {SCRAPING_AGENT_TOKEN}",
    "Content-Type": "application/json"
}

MAXIMUM_BATCH_SIZE = int(os.getenv('MAXIMUM_BATCH_SIZE'))
MAXIMUM_BATCHES_TO_PROCESS = int(os.getenv('MAXIMUM_BATCHES_TO_PROCESS'))

"""
Creating or Configuring Queue for DataIngestor
"""
app.conf.task_default_queue = "data_ingestor_queue"

"""
Celery tasks to automate.
"""
@app.task(name="celery_worker.print_hello")
def print_hello():
    print("Hello from Celery Beat!")

"""
Core workflow functions for the Data Ingestor service.

- start_scraping_listing: Pick oldest pending listings, trigger Scraping Agent, create status records.  
- create_product_batches: Group unbatched ProductURLs into available or new batches, save to DB.  
- scrape_batch: Process oldest batches, call Scraping Agent, track statuses, update batch state.  
- fetch_results: Check processing records, fetch results, ingest data, update statuses.

Together, these functions cover scheduling, batching, scraping, 
status tracking, and data ingestion.
"""
@app.task(name="celery_worker.start_scraping_listing")
def start_scraping_listing():
    """
    Trigger scraping for the oldest listing per source via Scraping Agent.
    Records job IDs in status tracker.
    """
    listings = listing_manager.get_oldest_listings_per_source()

    if not listings:
        logger.info("No listings found to scrape.")
        return
    for listing in listings:
        try:
            payload = {
                "webpage_url": listing['url'],
                "priority": "low",
                "type_page": "listing"
            }
            logger.info(f"Calling Scraping Agent for URL: {listing['url']}")
            response = requests.post(SCRAPING_AGENT_ENDPOINT + '/scrape', json=payload, headers=headers)
            if response.status_code == 200:
                job_id = response.json().get('job_id')
                logger.info(f"Scraping job created for {listing['url']}, job_id: {job_id}")

                status = Status(
                    id=str(uuid.uuid4()),
                    ingestion_type="listing",
                    job_id=job_id,
                    status="processing",
                    entity_id=listing['id']
                )
                status_manager.create_status(status)
            else:
                logger.error(
                    f"Failed to call Scraping Agent for {listing['url']}. "
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            logger.exception(f"Exception occurred while scraping {listing['url']}: {e}")

@app.task(name="celery_worker.create_product_batches")
def create_product_batches():
    unbatched_product_urls = product_url_manager.get_unbatched_product_urls()
    if not unbatched_product_urls:
        logger.info("[BATCH] No unbatched ProductUrls found. Nothing to do.")
        return []

    logger.info(f"[BATCH] Found {len(unbatched_product_urls)} unbatched ProductUrls")

    reusable_batch = batch_manager.get_batch_with_space(MAXIMUM_BATCH_SIZE)
    batches_created_or_updated = []

    if reusable_batch:
        empty_space = MAXIMUM_BATCH_SIZE - reusable_batch["batch_size"]
        assign_count = min(empty_space, len(unbatched_product_urls))
        urls_for_reuse = unbatched_product_urls[:assign_count]

        logger.info(f"[BATCH] Filling existing batch {reusable_batch['id']} with {len(urls_for_reuse)} ProductUrls")

        for url in urls_for_reuse:
            batch_manager.add_product_url(reusable_batch["id"], url["id"])
            product_url_manager.update_product_url(url["id"], {"batched": True,"batch_id":reusable_batch['id']})

        batches_created_or_updated.append(reusable_batch)
        unbatched_product_urls = unbatched_product_urls[assign_count:]

        if not unbatched_product_urls:
            logger.info("[BATCH] All unbatched ProductUrls assigned to existing batch.")
            return batches_created_or_updated

    while unbatched_product_urls:

        batch_urls = unbatched_product_urls[:MAXIMUM_BATCH_SIZE]
        unbatched_product_urls = unbatched_product_urls[MAXIMUM_BATCH_SIZE:]

        new_batch_id = str(uuid.uuid4())
        new_batch = Batch(
            id=new_batch_id,
            urls=[url["id"] for url in batch_urls],
            batch_size=len(batch_urls),
            last_processed=None
        )
        logger.info(f"[BATCH] Creating new batch {new_batch_id} with {len(batch_urls)} ProductUrls")
        batch_manager.create_batch(new_batch)

        for url in batch_urls:
            product_url_manager.update_product_url(url["id"], {"batched": True,"batch_id":new_batch_id})

        batches_created_or_updated.append(new_batch.model_dump())

    logger.info(f"[BATCH] Completed batching. {len(batches_created_or_updated)} batches created/updated.")

@app.task(name="celery_worker.scrape_batch")
def scrape_batch():
    batches_to_process = batch_manager.get_top_n_batches(MAXIMUM_BATCHES_TO_PROCESS)
    
    for batch in batches_to_process:
        urls = batch.get('urls', [])
        if not urls:
            logger.warning(f"[BATCH] Batch {batch['id']} has no URLs to process.")
            continue
        
        logger.info(f"[BATCH] Processing Batch {batch['id']} with {len(urls)} URLs.")
        
        for product_url_id in urls:
            try:
                product_url_doc = product_url_manager.get_product_url(product_url_id=product_url_id)
                product_url = product_url_doc.get('url')
                if not product_url:
                    logger.warning(f"[BATCH] URL not found for ID: {product_url_id}")
                    continue

                payload = {
                    "webpage_url": product_url,
                    "priority": "high",
                    "type_page": "product"
                }

                response = requests.post(
                    f"{SCRAPING_AGENT_ENDPOINT}/scrape",
                    json=payload,
                    headers=headers,
                    timeout=20
                )

                if response.status_code == 200:
                    job_id = response.json().get('job_id')
                    logger.info(f"[BATCH] Scraping job created for {product_url_id}, job_id: {job_id}")
                    status = Status(
                        id=str(uuid.uuid4()),
                        ingestion_type="product",
                        job_id=job_id,
                        status="processing",
                        entity_id=product_url_id
                    )
                    status_manager.create_status(status)
                else:
                    logger.error(
                        f"[BATCH] Failed to call Scraping Agent for {product_url_id}. "
                        f"Status code: {response.status_code}, Response: {response.text}"
                    )
            except Exception as e:
                logger.error(f"[BATCH] Exception while processing URL {product_url_id}: {e}")

        batch_manager.update_batch(
            batch_id=batch['id'],
            changes={"last_processed": str(datetime.now())}
        )
        logger.info(f"[BATCH] Finished processing Batch {batch['id']}")

@app.task(name="celery_worker.fetch_results")
def fetch_results():
    processing_statuses = status_manager.get_status_by_status('processing')

    for status in processing_statuses:
        status_id = status['id']
        job_id = status['job_id']
        entity_id = status['entity_id']

        try:
            fetch_url = f"{SCRAPING_AGENT_ENDPOINT}/scrape/{job_id}/status/"
            logger.info(f"Fetching Status for Job-ID : {job_id}")

            status_response = requests.get(fetch_url, headers=headers).json()
            logger.info(f"Fetched Status for Job-ID : {job_id}")

            job_status = status_response['status']
            entity_type = status_response['type_page']

            if job_status == 'completed':
                try:
                    fetch_result_url = f"{SCRAPING_AGENT_ENDPOINT}/scrape/{job_id}/result/"
                    result_response = requests.get(fetch_result_url, headers=headers).json()

                    if entity_type == 'listing':
                        source_id = listing_manager.get_listing(entity_id)['source_id']
                        product_urls = result_response['result']['items']

                        listing_manager.update_listing(
                            listing_id=entity_id,
                            changes={'last_listed': str(datetime.now())}
                        )

                        if not product_urls:
                            status_manager.update_status(status_id=status_id, changes={'status': 'completed'})
                        else:
                            for product_url in product_urls:
                                try:
                                    if product_url_manager.product_url_exists(url=product_url['url']):
                                        continue
                                    product_url_entity = ProductUrl(
                                        id=str(uuid.uuid4()),
                                        url=product_url['url'],
                                        source_id=source_id,
                                        listing_id=entity_id,
                                        page_index=product_url['page_rank']
                                    )
                                    product_url_manager.create_product_url(product_url_entity)
                                except Exception as e:
                                    logger.error(f"[LISTING] Failed inserting ProductUrl {product_url['url']}: {e}")

                        status_manager.update_status(status_id=status_id, changes={'status': 'completed'})

                    elif entity_type == 'product':
                        product_id = result_response['result']['id']
                        search_product = product_manager.get_product(product_id=product_id)

                        if search_product:
                            updates = {}
                            if result_response['result'].get('price') is not None:
                                updates["price"] = result_response['result']['price']
                            if result_response['result'].get('colors'):
                                updates["colors"] = result_response['result']['colors']
                            if result_response['result'].get('size'):
                                updates["size"] = result_response['result']['size']
                            if result_response['result'].get('rating') is not None:
                                updates["rating"] = result_response['result']['rating']
                            if result_response['result'].get('review_count') not in (None, 0):
                                updates["review_count"] = result_response['result']['review_count']
                            if result_response['result'].get('scraped_datetime') is not None:
                                updates["scraped_datetime"] = result_response['result']['scraped_datetime']
                            if result_response['result'].get('page_content'):
                                updates["page_content"] = result_response['result']['page_content']

                            if updates:
                                product_manager.update_product(product_id=product_id, changes=updates)

                            status_manager.update_status(status_id=status_id, changes={'status': 'completed'})

                        else:
                            product_url_doc = product_url_manager.get_product_url_by_url(
                                result_response['result']['url']
                            )
                            if not product_url_doc:
                                status_manager.update_status(status_id=status_id, changes={'status': 'failed'})
                                raise ValueError(f"No ProductUrl found for URL: {result_response['result']['url']}")

                            product = Product(
                                id=result_response['result']['id'],
                                url_id=product_url_doc["id"],
                                title=result_response['result']['title'],
                                price=float(result_response['result']['price']),
                                category=result_response['result']['category'],
                                gender=result_response['result']['gender'],
                                url=result_response['result']['url'],
                                image_url=result_response['result']['image_url'],
                                colors=result_response['result'].get('colors', []),
                                size=result_response['result'].get('size', []),
                                material=result_response['result'].get('material', ""),
                                description=result_response['result'].get('description', ""),
                                rating=result_response['result'].get('rating'),
                                review_count=result_response['result'].get('review_count', 0),
                                processed=False,
                                scraped_datetime=result_response['result']['scraped_datetime'],
                                processed_datetime=None,
                                page_index=product_url_doc.get("page_index", 0),
                                page_content=result_response['result'].get('page_content', "")
                            )
                            try:
                                product_manager.create_product(product=product)
                                status_manager.update_status(status_id=status_id, changes={'status': 'completed'})
                            except Exception as e:
                                logger.error(f"[RESULT PROCESSING] Failed for job {job_id}: {e}")
                                status_manager.update_status(status_id=status_id, changes={'status': 'failed'})

                except Exception as e:
                    logger.error(f"[RESULT PROCESSING] Failed for job {job_id}: {e}")
                    status_manager.update_status(status_id=status_id, changes={'status': 'failed'})

            elif job_status == 'failed':
                status_manager.update_status(status_id=status_id, changes={'status': 'failed'})

        except Exception as e:
            logger.error(f"[FETCH RESULTS] General failure for job {job_id}: {e}")
            status_manager.update_status(status_id=status_id, changes={'status': 'failed'})

"""
Creating Celery Beat to trigger a function call in a fixed schedules.
"""
app.conf.timezone = "Asia/Kolkata"
app.conf.enable_utc = False
app.conf.beat_schedule = {
    # Every day at 7:00 AM IST
    "daily-task-7am": {
        "task": "celery_worker.start_scraping_listing",
        "schedule": crontab(hour=7, minute=0),
    },
    # Every day at 7:00 PM IST
    "daily-task-7pm": {
        "task": "celery_worker.start_scraping_listing",
        "schedule": crontab(hour=19, minute=0),
    },

    # Every day at 8:00 AM IST
    "daily-task-8am": {
        "task": "celery_worker.create_product_batches",
        "schedule": crontab(hour=8, minute=0),
    },
    # Every day at 8:00 PM IST
    "daily-task-8pm": {
        "task": "celery_worker.create_product_batches",
        "schedule": crontab(hour=20, minute=0),
    },

    # Every day at 9:00 AM IST
    "daily-task-9am": {
        "task": "celery_worker.scrape_batch",
        "schedule": crontab(hour=9, minute=0),
    },
    # Every day at 9:00 PM IST
    "daily-task-9pm": {
        "task": "celery_worker.scrape_batch",
        "schedule": crontab(hour=21, minute=0),
    },

    # Every 15 minutes
    "task-every-15-minutes": {
        "task": "celery_worker.fetch_results",
        "schedule": 900.0,
    },
}

app.conf.broker_transport_options = {'polling_interval': 180}
