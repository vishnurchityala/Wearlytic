import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
from app.db import SourceManager, ListingsManager
from app.models import Source
from datetime import datetime
from uuid import uuid4

source_manager = SourceManager()
listings_mangaer = ListingsManager()

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = APIRouter()

templates = Jinja2Templates(directory="./app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def home(request: Request):
    """
    Home route (Dashboard page).

    - If a user is logged in (session contains 'user' key),
      render the dashboard with the username.
    - Otherwise, redirect to the login page.
    """
    username = request.session.get("user")
    if username:
        sources = source_manager.get_sources()
        listings = listings_mangaer.get_all_listings()
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "username": username,"sources":sources,"listings":listings}
        )
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)