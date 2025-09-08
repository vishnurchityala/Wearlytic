# app/main.py
from fastapi import FastAPI
from app.routes import BaseRouter, SecurityRouter, SourceRouter, ListingRouter, DashboardRouter
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="DataIngestor API")
app.add_middleware(SessionMiddleware, secret_key="vrcftw")
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

app.include_router(BaseRouter)
app.include_router(SecurityRouter)
app.include_router(SourceRouter)
app.include_router(ListingRouter)
app.include_router(DashboardRouter)