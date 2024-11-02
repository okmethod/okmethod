from fastapi import FastAPI

from src.routes import api

app = FastAPI()

app.include_router(
    api.router,
    prefix="/api",
    tags=["Root"],
)
