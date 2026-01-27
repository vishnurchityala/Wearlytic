import time
from datetime import datetime

from celery import Celery
from celery.utils.log import get_task_logger
from kombu import Queue

from scraperkit.utils import get_scraper_from_url, extract_domain
from scraperkit.utils import cache as ScraperCache
from api.db import JobsManager, JobResultsManager
from api.models import Listing, ListingItem, JobResult

from dotenv import load_dotenv
import os

load_dotenv()

logger = get_task_logger(__name__)

UPSTASH_REDIS_HOST = os.getenv("UPSTASH_REDIS_HOST")
UPSTASH_REDIS_PORT = os.getenv("UPSTASH_REDIS_PORT")
UPSTASH_REDIS_PASSWORD = os.getenv("UPSTASH_REDIS_PASSWORD")
RUN_TYPE_LOCAL = os.getenv("RUN_TYPE_LOCAL")
if RUN_TYPE_LOCAL == 'YES':
    connection_link ="redis://localhost:6379/0"
else:
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

"""
TODO:
Refactor Celery tasks to improve structure, clarity, and reliability:

1. Extract repetitive logic (e.g., job status updates, result creation, logging) into reusable helper functions.
2. Improve exception handling by logging full stack traces and handling scraper-specific errors more gracefully.
3. Make pagination and scraping loops more robust to prevent infinite loops or premature termination.
4. Ensure consistent use of 'completed_at' timestamps and accurate job status transitions.
5. Implement caching for scraper instances to avoid redundant instantiation and improve performance.
6. Add validation and sanitization for incoming URLs to prevent failures on invalid input.
"""
@celery_app.task(name="scrape.listing", bind=True)
def scrape_listing_task(self, url: str):
    job_manager = JobsManager()
    job_result_manager = JobResultsManager()
    job_id = self.request.id

    logger.warning(f"scrape.listing started | job_id={job_id} | url={url}")

    if not url:
        logger.error("scrape.listing called with empty url")
        job_manager.update_job(
            job_id=job_id,
            updates={"status": "failed", "completed_at": datetime.now()}
        )
        return "Scrape Listing Task failed : invalid url"

    job_manager.update_job(
        job_id=job_id,
        updates={"status": "processing"}
    )

    scraper = None
    items = []

    try:
        domain = extract_domain(url)
        scraper = get_scraper_from_url(url)

        current_url = url
        page_rank = 1
        page_count = 0
        max_pages = 30

        while current_url and page_count < max_pages:
            logger.info(f"Scraping page {page_count + 1} | url={current_url}")

            pagination = scraper.get_pagination_details(current_url)
            listings = scraper.get_product_listings(
                current_url,
                pagination.get("current_page")
            )

            if not listings:
                logger.warning(f"No listings found | url={current_url}")
                break

            for listing_url in listings:
                items.append(
                    ListingItem(
                        url=listing_url,
                        page_rank=page_rank
                    )
                )
                page_rank += 1

            next_url = pagination.get("next_page_url")
            if not next_url or next_url == current_url:
                break

            current_url = next_url
            page_count += 1

        listing_result = Listing(items=items)

        job_result_manager.create_result(
            JobResult(
                job_id=job_id,
                result=listing_result,
                status="completed",
                completed_at=datetime.now(),
                error_message=None
            )
        )

        job_manager.update_job(
            job_id=job_id,
            updates={
                "status": "completed",
                "completed_at": datetime.now()
            }
        )

        ScraperCache.insert(
            source_website=domain,
            scraper_object=scraper
        )

        logger.info(
            f"scrape.listing completed | job_id={job_id} | items={len(items)}"
        )
        return f"Scrape Listing Task completed : {url}"

    except Exception as exc:
        logger.exception(
            f"scrape.listing failed | job_id={job_id} | url={url}"
        )

        job_result_manager.create_result(
            JobResult(
                job_id=job_id,
                result=Listing(items=[]),
                status="failed",
                completed_at=datetime.now(),
                error_message=str(exc)
            )
        )

        job_manager.update_job(
            job_id=job_id,
            updates={
                "status": "failed",
                "completed_at": datetime.now()
            }
        )

        return f"Scrape Listing Task failed : {url}"


@celery_app.task(name="scrape.product", bind=True)
def scrape_product_task(self, url: str):
    job_manager = JobsManager()
    job_result_manager = JobResultsManager()
    job_id = self.request.id

    logger.warning(f"scrape.product started | job_id={job_id} | url={url}")

    if not url:
        logger.error("scrape.product called with empty url")
        job_manager.update_job(
            job_id=job_id,
            updates={"status": "failed", "completed_at": datetime.now()}
        )
        return "Scrape Product Task failed : invalid url"

    job_manager.update_job(
        job_id=job_id,
        updates={"status": "processing"}
    )

    scraper = None

    try:
        domain = extract_domain(url)
        scraper = get_scraper_from_url(url)

        logger.info(f"Scraping product | url={url}")

        product_details = scraper.get_product_details(
            product_page_url=url
        )

        product_details = product_details.model_dump(mode="json")

        job_result_manager.create_result(
            JobResult(
                job_id=job_id,
                result=product_details,
                status="completed",
                completed_at=datetime.now(),
                error_message=None
            )
        )

        job_manager.update_job(
            job_id=job_id,
            updates={
                "status": "completed",
                "completed_at": datetime.now()
            }
        )

        ScraperCache.insert(
            source_website=domain,
            scraper_object=scraper
        )

        logger.info(f"scrape.product completed | job_id={job_id}")
        return f"Scrape Product Task completed : {url}"

    except Exception as exc:
        logger.exception(
            f"scrape.product failed | job_id={job_id} | url={url}"
        )

        job_result_manager.create_result(
            JobResult(
                job_id=job_id,
                result={},
                status="failed",
                completed_at=datetime.now(),
                error_message=str(exc)
            )
        )

        job_manager.update_job(
            job_id=job_id,
            updates={
                "status": "failed",
                "completed_at": datetime.now()
            }
        )

        return f"Scrape Product Task failed : {url}"
