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


@router.get("/", response_class=HTMLResponse)
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

@router.post("/sources", response_class=HTMLResponse)
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

    source = Source(name=source_name,base_url=base_url,active=False,created_at=datetime.now(),id=str(uuid4()))
    source_manager.create_source(source=source)

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/sources/edit", response_class=HTMLResponse)
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
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    active_flag = active == "on"
    # TODO: Explicit Methods for DB is Source Turned Off.
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

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    """
    GET /login - Render the login page.

    - Initially passes an empty error message to the template.
    """
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": ""}
    )


@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    POST /login - Validate login credentials.

    - Compare submitted username and password with environment variables.
    - If valid, save 'username' into session and redirect to dashboard.
    - If invalid, reload login form with error message.
    """
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["user"] = username
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials!"}
    )


@router.post("/logout")
def logout_post(request: Request):
    """
    POST /logout - Clear session and redirect to login.

    - Explicitly clears all session data.
    - Ensures user is logged out after clicking a logout form/button.
    """
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
def logout_get(request: Request):
    """
    GET /logout - Clear session and redirect to login.

    - Provides a GET endpoint as well (in case logout is triggered by a link).
    """
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
