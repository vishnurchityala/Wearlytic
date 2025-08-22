from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="")

@router.get(path="/")
def index():
    return RedirectResponse(url="/api/")

@router.get(path="/api/")
def api_index():
    return {
        "message" : "Base URL Enpoint",
        "endpoints" : {
            "/api/scrape/":"POST",
            "/api/scrape/task_id/status":"GET",
            "/api/scraper/task_id/result" : "GET"
        }
    }