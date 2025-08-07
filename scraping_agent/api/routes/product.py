from fastapi import APIRouter, Query
from api.models import JobRequest
from celery_worker.tasks import scrape_product_task

router = APIRouter(prefix="/api/scrape/product")

@router.post("/")
def start_product_scrape(request : JobRequest):
    task = scrape_product_task.apply_async(args=[str(request.webpage_url)], queue='scrape_'+request.priority)
    return {"task_id" : task.id}
