from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException
from api.models import JobRequest, Job
from api.celery_worker import scrape_product_task, scrape_listing_task
from api.db import JobsManager
from api.security import verify_token

router = APIRouter(prefix="/api/scrapingagent/scrape")
job_manager = JobsManager()

@router.post("/",status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def start_scrape(request : JobRequest):

    if request.priority not in ['high','medium','low']:
        raise HTTPException(status_code=404, detail=f"Got Bad Priority Type")
    if request.type_page not in ['product','listing']:
        raise HTTPException(status_code=404, detail=f"Got Bad Page Type")
    
    if request.type_page == 'product':
        task = scrape_product_task.apply_async(args=[str(request.webpage_url)], queue='scraping_agent_scrape_'+request.priority)
    elif request.type_page == 'listing':
        task = scrape_listing_task.apply_async(args=[str(request.webpage_url)], queue='scraping_agent_scrape_'+request.priority)

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
