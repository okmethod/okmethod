from pydantic import BaseModel


class HeartbeatResponse(BaseModel):
    alive: str
