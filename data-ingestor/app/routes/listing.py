import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
from app.db import ListingsManager,SourceManager
from app.models import Listing
from datetime import datetime
from uuid import uuid4
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


listing_manager = ListingsManager()
source_manager = SourceManager()

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = APIRouter()

templates = Jinja2Templates(directory="./app/templates")


@router.post("/api/listings", response_class=HTMLResponse)
def create_listing(
    request: Request,
    listing_url: str = Form(...),
    source_id: str = Form(...)
):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    source = source_manager.get_source(source_id=source_id)
    listing = Listing(id=str(uuid4()),source_id=source_id,url=listing_url,last_listed=None,active=source["active"])
    listing_manager.create_listing(listing=listing)
    source_manager.add_listing_to_source(listing.source_id,listing.id)

    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/api/listings/edit", response_class=HTMLResponse)
def edit_listing(
    request: Request,
    listing_id: str = Form(...),
    listing_url: str = Form(...)
):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


    changes = {
        "url": listing_url,
    }

    listing_manager.update_listing(
        listing_id=listing_id,
        changes=changes
    )

    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/api/listings/delete", response_class=HTMLResponse)
def delete_listing(
    request: Request,
    listing_id: str = Form(...),

):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    # Testing Changes =======>
    source_id = listing_manager.get_listing(listing_id=listing_id)['source_id']
    source_manager.remove_listing_from_source(source_id=source_id,listing_id=listing_id)
    listing_manager.delete_listing(listing_id=listing_id)

    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)