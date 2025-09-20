"""
Importing Modules for Celery Workers.
"""
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from app.db import ListingsManager, StatusManager, SourceManager, ProductUrlManager
from app.models import Status, ProductUrl
from dotenv import load_dotenv
import requests
from datetime import datetime
import hashlib
import uuid
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

def create_product_batches():
    # TODO: Retrieve all ProductURLs that have not yet been assigned to a batch.
    # TODO: Identify existing batches with available capacity.
    # TODO: Assign unbatched ProductURLs to these partially filled batches.
    # TODO: Create new batches for any remaining ProductURLs.
    # TODO: Save all batches and persist them in the database.
    pass

def scrape_batch():
    # TODO: Retrieve the N oldest unprocessed batches.
    # TODO: For each ProductURL in the batch, trigger a ScrapingAgent API call.
    # TODO: Create a status record for each ProductURL request.
    # TODO: Update the batch record to reflect its current processing state.
    pass

@app.task(name="celery_worker.fetch_results")
def fetch_results():
    processing_statuses = status_manager.get_status_by_status('processing')
    for status in processing_statuses:
        status_id = status['id']
        fetch_url = SCRAPING_AGENT_ENDPOINT+"/scrape/"+status['job_id']+"/status/"
        logger.info(f"Fetching Status for Job-ID : {status['job_id']}")
        status_response = requests.get(fetch_url,headers=headers).json()
        entity_id = status['entity_id']
        source_id = listing_manager.get_listing(entity_id)['source_id']
        logger.info(f"Fetched Status for Job-ID : {status['job_id']}")
        job_status = status_response['status']
        entity_type = status_response['type_page']
        if job_status == 'completed':
            fetch_result_url = SCRAPING_AGENT_ENDPOINT+"/scrape/"+status['job_id']+"/result/"
            result_response = requests.get(fetch_result_url,headers=headers).json()
            status_manager.update_status(status_id=status_id,changes={'status':'completed'})
            if entity_type == 'listing':
                product_urls = result_response['result']['items']
                listing_manager.update_listing(listing_id=entity_id,changes={'last_listed':str(datetime.now())})
                for product_url in product_urls:
                    if product_url_manager.product_url_exists(url=product_url['url']):
                        continue
                    product_url_entity = ProductUrl(id=str(uuid.uuid4()),url=product_url['url'],source_id= source_id,listing_id=entity_id,page_index=product_url['page_rank'])
                    try:
                        product_url_manager.create_product_url(product_url_entity)
                    except Exception as e:
                        print(product_url['url'])
            elif entity_type == 'product':
                # TODO: Product Ingestion Handled
                pass
        elif job_status == 'failed':
            status_manager.update_status(status_id=status_id,changes={'status':'failed'})

"""
Creating Celery Beat to trigger a function call in a fixed schedules.
"""
app.conf.beat_schedule = {
    # Every 10 seconds
    "print-hello-every-10-seconds": {
        "task": "celery_worker.print_hello",
        "schedule": 10.0,
    },

    # Every day at 7:00 AM
    "daily-task-7am": {
        "task": "celery_worker.start_scraping_listing",
        "schedule": crontab(hour=7, minute=0),
    },

    # Every day at 1:00 AM
    "daily-task-1am": {
        "task": "celery_worker.start_scraping_listing",
        "schedule": crontab(hour=1, minute=0),
    },

    # Every 15 minute
    "task-every-1-minute": {
        "task": "celery_worker.fetch_results",
        "schedule": 900.0,
    },
}
app.conf.broker_transport_options = {'polling_interval': 60}
