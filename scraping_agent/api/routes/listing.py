from fastapi import APIRouter, Query
from api.models import JobRequest
from celery_worker.tasks import scrape_listing_task
router = APIRouter(prefix="/api/scrape/listing")

@router.post("/")
async def start_listing_scrape(request : JobRequest):
    task = scrape_listing_task.apply_async(args=[str(request.webpage_url)], queue='scrape_medium')
    return {"task_id" : task.id}
