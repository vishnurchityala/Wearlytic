"""
Importing Modules for Celery Workers.
"""
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

"""
Creating Logger fot the Tasks.
"""
logger = get_task_logger(__name__)

"""
Celery Queue Configuration.
"""
app = Celery(
    "dataingestor",
    broker="redis://localhost:6379/0",
    backend = 'rpc://'
)

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
def start_scraping_listing():
    # TODO: Retrieve the oldest pending (unscraped) listing from each source.
    # TODO: Trigger the Scraping Agent via API request.
    # TODO: Record the Celery task IDs (AsyncIDs) in the status tracker.
    # TODO: Create and persist status objects in the database.
    pass

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

def fetch_results():
    # TODO: Query the database for all records with status = "processing".
    # TODO: For each record, fetch the latest result from the Scraping Agent.
    # TODO: Determine the ingestion type and insert the data into the database.
    # TODO: Update the record’s status in the database based on the response.
    pass


"""
Creating Celery Beat to trigger a function call in a fixed schedules.
"""
app.conf.beat_schedule = {
    "print-hello-every-10-seconds": {
        "task": "celery_worker.print_hello",
        "schedule": 10.0,
    },
}