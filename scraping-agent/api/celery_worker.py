import time
from datetime import datetime

from celery import Celery
from celery.utils.log import get_task_logger
from kombu import Queue

from scraperkit.utils import get_scraper_from_url
from api.db import JobsManager, JobResultsManager
from api.models import Listing, ListingItem, JobResult

from dotenv import load_dotenv
import os

load_dotenv()

logger = get_task_logger(__name__)

UPSTASH_REDIS_HOST = os.getenv("UPSTASH_REDIS_HOST")
UPSTASH_REDIS_PORT = os.getenv("UPSTASH_REDIS_PORT")
UPSTASH_REDIS_PASSWORD = os.getenv("UPSTASH_REDIS_PASSWORD")
connection_link = f"rediss://:{UPSTASH_REDIS_PASSWORD}@{UPSTASH_REDIS_HOST}:{UPSTASH_REDIS_PORT}?ssl_cert_reqs=none"

celery_app = Celery(
    "scrapingagent",
    broker=connection_link,
    backend = 'rpc://'
)

celery_app.conf.task_queues = [
    Queue("scraping_agent_scrape_high"),
    Queue("scraping_agent_scrape_medium"),
    Queue("scraping_agent_scrape_low"),
]
celery_app.conf.task_default_queue = "scraping_agent_scrape_medium"
celery_app.conf.broker_transport_options = {'polling_interval': 60}


@celery_app.task(name="scrape.listing", bind=True)
def scrape_listing_task(self, url: str):
    job_manager = JobsManager()
    job_result_manager = JobResultsManager()
    logger.info(f"Task ID: {self.request.id}")
    time.sleep(1)
    job_manager.update_job(job_id=self.request.id,updates={"status":"processing"})
    scraper = get_scraper_from_url(url)
    try:
        count = 1
        page_count = 1
        listing_result = []
        while url != None and page_count < 30:
            listing_details = scraper.get_pagination_details(url)
            listings = scraper.get_product_listings(url,listing_details['current_page'])
            logger.info(f"Scraping : {url}")
            for listing in listings:
                listing_result.append(ListingItem(
                    url=listing,
                    page_rank=count
                ))
                count+=1
            url = listing_details['next_page_url']
            page_count += 1
        listing_result = Listing(items=listing_result)
        result = JobResult(
            job_id=self.request.id,
            result=listing_result,
            status='completed',
            completed_at=datetime.now(),
            error_message=None
        )
        job_result_manager.create_result(result)
        job_manager.update_job(job_id=self.request.id,updates={"status":"completed"})
    except Exception as e:
        result = JobResult(
            job_id=self.request.id,
            result=Listing(
                items=[]
            ),
            status='failed',
            completed_at=datetime.now(),
            error_message= str(e)
        )
        job_result_manager.create_result(result)
        job_manager.update_job(job_id=self.request.id,updates={"status":"failed","completed_at":datetime.now()})
        return f"Scrape Listing Task : {url}"

    return f"Scrape Listing Task : {url}"

@celery_app.task(name="scrape.product", bind=True)
def scrape_product_task(self, url: str):
    job_manager = JobsManager()
    job_result_manager = JobResultsManager()
    logger.info(f"Task ID: {self.request.id}")
    time.sleep(1)
    job_manager.update_job(job_id=self.request.id,updates={"status":"processing"})
    scraper = get_scraper_from_url(url)
    try:
        product_details = scraper.get_product_details(product_page_url=url)
        product_details = product_details.model_dump(mode="json")
        result = JobResult(
            job_id=self.request.id,
            result=product_details,
            status='completed',
            completed_at=datetime.now(),
            error_message= None
        )
        job_result_manager.create_result(result)
        job_manager.update_job(job_id=self.request.id,updates={"status":"completed","completed_at":datetime.now()})
    except Exception as e:
        result = JobResult(
            job_id=self.request.id,
            result=[],
            status='failed',
            completed_at=datetime.now(),
            error_message= str(e)
        )
        job_result_manager.create_result(result)
        job_manager.update_job(job_id=self.request.id,updates={"status":"failed","completed_at":datetime.now()})
        return f"Scrape Product Task : {url}"

    time.sleep(20)
    job_manager.update_job(job_id=self.request.id,updates={"status":"completed","completed_at":datetime.now()})
    return f"Scrape Product Task : {url}"
