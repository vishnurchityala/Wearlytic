from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from ..celery_worker import scrape_batch, fetch_results, start_scraping_listing, create_product_batches

router = APIRouter(prefix="/api", tags=["batch"])

@router.post("/trigger-batch-scrape")
async def trigger_batch_scrape():
    scrape_batch.delay()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/trigger-batch-create")
async def trigger_batch_create():
    create_product_batches.delay()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/trigger-status-update")
async def trigger_status_update():
    fetch_results.delay()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/trigger-listing-scrape")
async def trigger_listing_scrape():
    start_scraping_listing.delay()
    return RedirectResponse(url="/dashboard", status_code=303)
