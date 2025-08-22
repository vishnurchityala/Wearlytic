# app/main.py
from fastapi import FastAPI
from api.routes import ScrapeRouter, StatusRouter, IndexRouter

app = FastAPI(title="ScrapingAgent API")

app.include_router(IndexRouter)
app.include_router(ScrapeRouter)
app.include_router(StatusRouter)
