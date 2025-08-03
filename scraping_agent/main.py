# app/main.py
from fastapi import FastAPI
from api.routes import ListingRouter, ProductRouter, StatusRouter

app = FastAPI(title="ScrapingAgent API")

app.include_router(ListingRouter)
app.include_router(ProductRouter)
app.include_router(StatusRouter)