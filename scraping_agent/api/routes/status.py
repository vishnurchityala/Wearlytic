from fastapi import APIRouter, HTTPException
from api.models import JobResult, Product, Listing
from api.db import JobsManager, JobResultsManager
from datetime import datetime

router = APIRouter(prefix="/api/scrape")
job_manager = JobsManager()
job_result_manager = JobResultsManager()

@router.get("/listing/{task_id}/status/")
def get_listing_status(task_id: str):
    try:
        job = job_manager.get_job(task_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job {task_id} not found")


@router.get("/listing/{task_id}/result/")
def get_listing_result(task_id: str) -> JobResult:
    try:
        result = job_result_manager.get_result(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Job {task_id} not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job {task_id} not found")

@router.get("/product/{task_id}/status/")
def get_product_status(task_id: str):
    try:
        job = job_manager.get_job(task_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job {task_id} not found")

@router.get("/product/{task_id}/result/")
def get_product_result(task_id: str)-> JobResult:
    try:
        result = job_result_manager.get_result(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Job {task_id} not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job {task_id} not found")

