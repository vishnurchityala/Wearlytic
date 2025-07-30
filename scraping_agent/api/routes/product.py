from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/scrape/product")

@router.post("/")
def start_product_scrape(url: str = Query(...)):
    return {"task_id": "Dummy Task ID"}
