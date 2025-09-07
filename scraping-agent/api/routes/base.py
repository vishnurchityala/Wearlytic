from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="")

@router.get("/", summary="Root redirect")
def index():
    """Redirect root URL to the ScrapingAgent API base endpoint."""
    return RedirectResponse(url="/api/scrapingagent/")

@router.get("/api/scrapingagent/", summary="ScrapingAgent base endpoint")
def api_index():
    """Return available API endpoints for ScrapingAgent."""
    return {
        "message": "Base URL Endpoint",
        "endpoints": {
            "POST /api/scrape/": "Start a new scraping task",
            r"GET /api/scrape/{task_id}/status": "Check the status of a scraping task",
            r"GET /api/scraper/{task_id}/result": "Fetch the result of a scraping task",
        },
    }
