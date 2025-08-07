from scraping_agent_celery_app import celery_app
from scraperkit.utils import get_scraper_from_url

@celery_app.task(name="scrape.listing")
def scrape_listing_task(url: str):
    return f"Scrape Listing Task : {url}"

@celery_app.task(name="scrape.product")
def scrape_product_task(url: str):
    return f"Scrape Product Task : {url}"
