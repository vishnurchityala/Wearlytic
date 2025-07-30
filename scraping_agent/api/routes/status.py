from fastapi import APIRouter

router = APIRouter(prefix="/api/scrape")

@router.get("/listing/{task_id}/status/")
def get_listing_status(task_id: str):
    return {"message": "Dummy status response for listing"}

@router.get("/listing/{task_id}/result/")
def get_listing_result(task_id: str):
    return {
        "message": "Dummy result response for listing",
        "data": "Some dummy data"
    }

@router.get("/product/{task_id}/status/")
def get_product_status(task_id: str):
    return {"message": "Dummy status response for product"}

@router.get("/product/{task_id}/result/")
def get_product_result(task_id: str):
    return {
        "message": "Dummy result response for product",
        "data": "Some dummy data"
    }
