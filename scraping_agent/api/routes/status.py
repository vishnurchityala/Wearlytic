from fastapi import APIRouter
from api.models import JobResult, Product, Listing
from datetime import datetime

router = APIRouter(prefix="/api/scrape")

@router.get("/listing/{task_id}/status/")
def get_listing_status(task_id: str):
    return {"message": "Dummy status response for listing"}

@router.get("/listing/{task_id}/result/")
def get_listing_result(task_id: str) -> JobResult:
    dummy_result = JobResult(
        job_id=task_id,
        result=Listing(),
        status="completed",
        completed_at=datetime.utcnow(),
        error_message=None
    )
    return dummy_result

@router.get("/product/{task_id}/status/")
def get_product_status(task_id: str):
    return {"message": "Dummy status response for product"}

@router.get("/product/{task_id}/result/")
def get_product_result(task_id: str)-> JobResult:
    dummy_result = JobResult(
        job_id=task_id,
        result=Product(),
        status="completed",
        completed_at=datetime.utcnow(),
        error_message=None
    )
    return dummy_result
