import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
from app.db import SourceManager, ListingsManager, StatusManager, ProductUrlManager, BatchManager, ProductManager
from collections import Counter
from app.models import Source
from datetime import datetime
from uuid import uuid4

source_manager = SourceManager()
listings_mangaer = ListingsManager()
status_manager = StatusManager()
product_url_mangaer = ProductUrlManager()
batch_manager = BatchManager()
product_manager = ProductManager()

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
        statuses = status_manager.get_all_status()
        product_urls = product_url_mangaer.get_all_product_urls()
        batches = batch_manager.get_all_batches()
        status_bar_graph_data_dict = {
            "Completed": 0,
            "Processing": 0,
            "Failed": 0
        }
        products_count = product_manager.get_products_count()
        for status in statuses:
            if status['status'] == 'completed':
                status_bar_graph_data_dict['Completed'] += 1
            elif status['status'] == 'processing':
                status_bar_graph_data_dict['Processing'] += 1
            elif status['status'] == 'failed':
                status_bar_graph_data_dict['Failed'] += 1
        status_bar_chart_data = {
            "labels": list(status_bar_graph_data_dict.keys()),
            "values": list(status_bar_graph_data_dict.values())
        }
        source_distribution = Counter(p["source_id"] for p in product_urls)
        source_distribution_named = {}
        for source_id, count in source_distribution.items():
            source_name = source_manager.get_source_name(source_id) or source_id
            source_distribution_named[source_name] = count
        source_pie_chart_data = {
            "labels": list(source_distribution_named.keys()),
            "values": list(source_distribution_named.values()),
        }
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "username": username,
                "sources": sources,
                "listings": listings,
                "statuses": statuses,
                "product_urls": product_urls,
                "status_bar_chart_data": status_bar_chart_data,
                "source_pie_chart_data": source_pie_chart_data,
                "batches": batches,
                "products_count": products_count
            }
        )
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)