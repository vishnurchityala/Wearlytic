from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="")

@router.get("/", summary="Root redirect")
def index():
    """Redirect root URL to the DataIngestor API base endpoint."""
    return RedirectResponse(url="/api/dataingestor/")

@router.get("/api/dataingestor/", summary="DataIngestor base endpoint")
def api_index():
    """Return available API endpoints for DataIngestor."""
    return {
        "message": "Base URL Endpoint",
        "endpoints": {
            "GET /api/sources": "Fetch all sources",
            "GET /api/listings": "Fetch all listings",
        },
    }
