from datetime import datetime
from fastapi import APIRouter, status
from api.models import JobRequest, Job
from api.celery_worker import scrape_product_task
from api.db import JobsManager, JobResultsManager

router = APIRouter(prefix="/api/scrape/product")
job_manager = JobsManager()

@router.post("/",status_code=status.HTTP_200_OK)
def start_product_scrape(request : JobRequest):
    print(request.webpage_url)
    task = scrape_product_task.apply_async(args=[str(request.webpage_url)], queue='scrape_'+request.priority)
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
    job_manager.create_job(job=job)
    return {"job_id" : task.id}
