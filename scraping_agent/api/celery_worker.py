import logging
import time

from celery import Celery
from celery.utils.log import get_task_logger
from kombu import Queue

from scraperkit.utils import get_scraper_from_url
logger = get_task_logger(__name__)

celery_app = Celery(
    "scrapingagent",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.task_queues = [
    Queue("scrape_high"),
    Queue("scrape_medium"),
    Queue("scrape_low"),
]
celery_app.conf.task_default_queue = "scrape_medium"

@celery_app.task(name="scrape.listing", bind=True)
def scrape_listing_task(self, url: str):
    logger.info(f"Task ID: {self.request.id}")
    # scraping logic here
    time.sleep(20)
    return f"Scrape Listing Task : {url}"

@celery_app.task(name="scrape.product", bind=True)
def scrape_product_task(self, url: str):
    logger.info(f"Task ID: {self.request.id}")
    # scraping logic here
    time.sleep(20)
    return f"Scrape Product Task : {url}"
