from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/scrape/listing")

@router.post("/")
def start_listing_scrape(url: str = Query(...)):
    return {"task_id": "Dummy Task ID"}
