from fastapi import FastAPI

from src.routes import heartbeat

app = FastAPI()

app.include_router(
    heartbeat.router,
    prefix="/api/heartbeat",
    tags=["Root"],
)
