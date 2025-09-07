import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = APIRouter()
templates = Jinja2Templates(directory="./app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    username = request.session.get("user")
    if username:
        return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["user"] = username
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials!"})

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
