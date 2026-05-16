import logging
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, status, Depends, HTTPException
from api.models import JobRequest, Job
from api.celery_worker import scrape_product_task, scrape_listing_task
from api.db import JobsManager
from api.security import verify_token

router = APIRouter(prefix="/api/scrapingagent/scrape",redirect_slashes=False)
job_manager = JobsManager()
logger = logging.getLogger(__name__)

@router.post("/",status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def start_scrape(request : JobRequest):

    if request.priority not in ['high','medium','low']:
        raise HTTPException(status_code=404, detail=f"Got Bad Priority Type")
    if request.type_page not in ['product','listing']:
        raise HTTPException(status_code=404, detail=f"Got Bad Page Type")
    
    task_handler = scrape_product_task if request.type_page == 'product' else scrape_listing_task
    task_id = str(uuid4())

    job = Job(
        job_id=task_id,
        webpage_url=request.webpage_url,
        priority=request.priority,
        type_page=request.type_page,
        status='queued',
        created_at=datetime.now(),
        completed_at=None,
        error_message=None 
              )
    job_manager.create_job(job=job)

    try:
        task_handler.apply_async(
            args=[str(request.webpage_url)],
            queue='scraping_agent_scrape_'+request.priority,
            task_id=task_id,
        )
    except Exception as exc:
        logger.exception(f"Failed to enqueue scraping job {task_id}")
        try:
            job_manager.delete_job(task_id)
        except Exception:
            logger.exception(f"Failed to cleanup queued job record {task_id} after enqueue error")
        raise HTTPException(status_code=503, detail="Failed to queue scraping task") from exc

    return {"job_id" : task_id}
