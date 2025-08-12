# app/main.py
from fastapi import FastAPI
from api.routes import ScrapeRouter, StatusRouter

app = FastAPI(title="ScrapingAgent API")

app.include_router(ScrapeRouter)
app.include_router(StatusRouter)