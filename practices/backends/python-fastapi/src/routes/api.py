from datetime import datetime, timezone

from fastapi import APIRouter

from src.schemas.heartbeat import HeartbeatResponse

router = APIRouter()


@router.get(
    path="/heartbeat",
    response_model=HeartbeatResponse,
)
def heartbeat() -> HeartbeatResponse:
    now = datetime.now(tz=timezone.utc).isoformat()
    return HeartbeatResponse(alive=now)
