from datetime import datetime

from fastapi import APIRouter

from src.schemas.heartbeat import HeartbeatResponse

router = APIRouter()


@router.get(
    path="/heartbeat",
    response_model=HeartbeatResponse,
)
def heartbeat() -> HeartbeatResponse:
    now = datetime.utcnow().isoformat()
    return HeartbeatResponse(alive=now)
