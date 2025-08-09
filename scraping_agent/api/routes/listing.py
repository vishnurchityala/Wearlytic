from fastapi import APIRouter, Query
from api.models import JobRequest, Job
from api.celery_worker import scrape_listing_task
from datetime import datetime

router = APIRouter(prefix="/api/scrape/listing")

@router.post("/")
async def start_listing_scrape(request : JobRequest):
    task = scrape_listing_task.apply_async(args=[str(request.webpage_url)], queue='scrape_'+request.priority)
    job = Job(
        job_id=task.id,
        webpage_url=request.webpage_url,
        priority=request.priority,
        type_page=request.type_page,
        status='queued',
        created_at=datetime.now(),
        completed_at=None,
        error_message=None 
              )
    # Save the Job Object.
    return {"task_id" : task.id}
