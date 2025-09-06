# app/main.py
from fastapi import FastAPI
from api.routes import BaseRouter

app = FastAPI(title="DataIngestor API")

app.include_router(BaseRouter)