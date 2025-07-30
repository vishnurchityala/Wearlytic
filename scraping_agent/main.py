# app/main.py
from fastapi import FastAPI
from api.routes import listing, product, status

app = FastAPI(title="ScraperKit API")

app.include_router(listing.router)
app.include_router(product.router)
app.include_router(status.router)
