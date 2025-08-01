from fastapi import APIRouter, Query
from api.models import JobRequest
router = APIRouter(prefix="/api/scrape/listing")

@router.post("/")
def start_listing_scrape(request : JobRequest):
    return {"task_id": "Dummy Task ID"}