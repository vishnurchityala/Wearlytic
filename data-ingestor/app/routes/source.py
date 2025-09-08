import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
from app.db import SourceManager, ListingsManager
from app.models import Source
from datetime import datetime
from uuid import uuid4
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

source_manager = SourceManager()
listing_manager = ListingsManager()

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = APIRouter()

templates = Jinja2Templates(directory="./app/templates")


@router.post("/api/sources", response_class=HTMLResponse)
def create_source(
    request: Request,
    source_name: str = Form(...),
    base_url: str = Form(...)
):
    """
    Handle creation of a new source from dashboard form submission.

    - Validate and create new source using source_manager.
    - Then redirect back to the dashboard page.
    """
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    source = Source(name=source_name,listing_count=0,base_url=base_url,active=False,created_at=datetime.now(),id=str(uuid4()))
    source_manager.create_source(source=source)

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/api/sources/edit", response_class=HTMLResponse)
def edit_source(
    request: Request,
    source_id: str = Form(...),
    source_name: str = Form(...),
    base_url: str = Form(...),
    active: str = Form(None)
):
    """
    Handle editing/updating a source.

    - Requires the source ID and updated data.
    - Updates source in backend.
    - Redirects back to dashboard.
    """
    logging.info(f"EDIT ENDPOINT CALLED with source_id: {source_id}")  # Add this line

    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    active_flag = active == "on"
    listings = source_manager.get_source(source_id=source_id)["listings"]
    
    for listing in listings:
        listing_manager.update_listing(listing_id=listing,changes={"active": active_flag})

    changes = {
        "name": source_name,
        "base_url": base_url,
        "active": active_flag
    }

    source_manager.update_source(
        source_id=source_id,
        changes=changes
    )

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/api/sources/delete", response_class=HTMLResponse)
def delete_source(
    request: Request,
    source_id: str = Form(...),
):
    """
    Handle editing/updating a source.

    - Requires the source ID and updated data.
    - Updates source in backend.
    - Redirects back to dashboard.
    """
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    # TODO: Explicit Methods for DB is Source Turned Off.
    source_manager.delete_source(source_id=source_id)

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)