# app/main.py
from fastapi import FastAPI
from app.routes import BaseRouter, SecurityRouter
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="DataIngestor API")
app.add_middleware(SessionMiddleware, secret_key="vrcftw")
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

app.include_router(BaseRouter)
app.include_router(SecurityRouter)