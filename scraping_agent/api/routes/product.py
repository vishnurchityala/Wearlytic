from fastapi import APIRouter, Query
from api.models import JobRequest

router = APIRouter(prefix="/api/scrape/product")

@router.post("/")
def start_product_scrape(request : JobRequest):
    return {"task_id": "Dummy Task ID"}
