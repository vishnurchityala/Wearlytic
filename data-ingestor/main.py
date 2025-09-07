# app/main.py
from fastapi import FastAPI
from app.routes import BaseRouter, SecurityRouter
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI(title="DataIngestor API")
app.add_middleware(SessionMiddleware, secret_key="vrcftw")

app.include_router(BaseRouter)
app.include_router(SecurityRouter)