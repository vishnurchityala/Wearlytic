from datetime import datetime
from typing import Any

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

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
connection_link = os.getenv("REDIS_URL", "").strip() or DEFAULT_REDIS_URL
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


def _update_job_processing(job_manager: JobsManager, job_id: str) -> None:
    """Mark a job as actively processing and clear prior errors."""
    job_manager.update_job(
        job_id=job_id,
        updates={"status": "processing", "error_message": None}
    )


def _update_job_finished(
    job_manager: JobsManager,
    job_id: str,
    status: str,
    error_message: str | None = None,
) -> None:
    """Persist the final job status, completion time, and optional error."""
    job_manager.update_job(
        job_id=job_id,
        updates={
            "status": status,
            "completed_at": datetime.now(),
            "error_message": error_message,
        }
    )


def _create_job_result(
    job_result_manager: JobResultsManager,
    job_id: str,
    result: Any,
    status: str,
    error_message: str | None = None,
) -> None:
    """Store a finished job result payload with its completion metadata."""
    job_result_manager.create_result(
        JobResult(
            job_id=job_id,
            result=result,
            status=status,
            completed_at=datetime.now(),
            error_message=error_message,
        )
    )


def _persist_failure_state(
    job_manager: JobsManager,
    job_result_manager: JobResultsManager,
    job_id: str,
    result: Any,
    error_message: str,
) -> None:
    """Best-effort persistence for failed jobs and their failure result."""
    try:
        _update_job_finished(
            job_manager=job_manager,
            job_id=job_id,
            status="failed",
            error_message=error_message,
        )
    except Exception:
        logger.exception(f"Failed to update failed job state | job_id={job_id}")

    try:
        _create_job_result(
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=result,
            status="failed",
            error_message=error_message,
        )
    except Exception:
        logger.exception(f"Failed to persist failed job result | job_id={job_id}")


def _close_scraper(scraper, source_website: str | None) -> None:
    """Close scraper resources and log cleanup failures."""
    if scraper is None:
        return

    try:
        scraper.close()
    except Exception:
        logger.exception(
            f"Failed to close scraper resources | source={source_website or 'unknown'}"
        )


def _finalize_scraper(scraper, source_website: str | None, cache_on_success: bool) -> None:
    """Cache a reusable scraper after success, otherwise close it."""
    if scraper is None:
        return

    if cache_on_success and source_website:
        try:
            ScraperCache.insert(
                source_website=source_website,
                scraper_object=scraper,
            )
            return
        except Exception:
            logger.exception(
                f"Failed to cache scraper after successful task | source={source_website}"
            )

    _close_scraper(scraper, source_website)


def _run_listing_job(
    job_id: str,
    url: str,
    job_manager: JobsManager | None = None,
    job_result_manager: JobResultsManager | None = None,
) -> str:
    """Run the listing scrape flow, including pagination and result persistence."""
    job_manager = job_manager or JobsManager()
    job_result_manager = job_result_manager or JobResultsManager()

    logger.warning(f"scrape.listing started | job_id={job_id} | url={url}")

    if not url:
        error_message = "invalid url"
        logger.error("scrape.listing called with empty url")
        _persist_failure_state(
            job_manager=job_manager,
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=Listing(items=[]),
            error_message=error_message,
        )
        return "Scrape Listing Task failed : invalid url"

    scraper = None
    domain = None
    items = []
    success = False

    try:
        _update_job_processing(job_manager=job_manager, job_id=job_id)

        domain = extract_domain(url)
        scraper = get_scraper_from_url(url)

        current_url = url
        page_rank = 1
        page_count = 0
        max_pages = 30

        while current_url and page_count < max_pages:
            logger.info(f"Scraping page {page_count + 1} | url={current_url}")

            pagination = scraper.get_pagination_details(current_url)
            listings = scraper.get_product_listings(current_url)

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

        _create_job_result(
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=Listing(items=items),
            status="completed",
        )
        _update_job_finished(job_manager=job_manager, job_id=job_id, status="completed")
        success = True

        logger.info(
            f"scrape.listing completed | job_id={job_id} | items={len(items)}"
        )
        return f"Scrape Listing Task completed : {url}"

    except Exception as exc:
        logger.exception(
            f"scrape.listing failed | job_id={job_id} | url={url}"
        )
        _persist_failure_state(
            job_manager=job_manager,
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=Listing(items=[]),
            error_message=str(exc),
        )
        return f"Scrape Listing Task failed : {url}"

    finally:
        _finalize_scraper(scraper=scraper, source_website=domain, cache_on_success=success)


def _run_product_job(
    job_id: str,
    url: str,
    job_manager: JobsManager | None = None,
    job_result_manager: JobResultsManager | None = None,
) -> str:
    """Run the product scrape flow and persist the extracted product details."""
    job_manager = job_manager or JobsManager()
    job_result_manager = job_result_manager or JobResultsManager()

    logger.warning(f"scrape.product started | job_id={job_id} | url={url}")

    if not url:
        error_message = "invalid url"
        logger.error("scrape.product called with empty url")
        _persist_failure_state(
            job_manager=job_manager,
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=[],
            error_message=error_message,
        )
        return "Scrape Product Task failed : invalid url"

    scraper = None
    domain = None
    success = False

    try:
        _update_job_processing(job_manager=job_manager, job_id=job_id)

        domain = extract_domain(url)
        scraper = get_scraper_from_url(url)

        logger.info(f"Scraping product | url={url}")

        product_details = scraper.get_product_details(
            product_page_url=url
        ).model_dump(mode="json")

        _create_job_result(
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=product_details,
            status="completed",
        )
        _update_job_finished(job_manager=job_manager, job_id=job_id, status="completed")
        success = True

        logger.info(f"scrape.product completed | job_id={job_id}")
        return f"Scrape Product Task completed : {url}"

    except Exception as exc:
        logger.exception(
            f"scrape.product failed | job_id={job_id} | url={url}"
        )
        _persist_failure_state(
            job_manager=job_manager,
            job_result_manager=job_result_manager,
            job_id=job_id,
            result=[],
            error_message=str(exc),
        )
        return f"Scrape Product Task failed : {url}"

    finally:
        _finalize_scraper(scraper=scraper, source_website=domain, cache_on_success=success)


@celery_app.task(name="scrape.listing", bind=True)
def scrape_listing_task(self, url: str):
    """Celery entrypoint for listing-page scraping jobs."""
    return _run_listing_job(job_id=self.request.id, url=url)


@celery_app.task(name="scrape.product", bind=True)
def scrape_product_task(self, url: str):
    """Celery entrypoint for single-product scraping jobs."""
    return _run_product_job(job_id=self.request.id, url=url)
