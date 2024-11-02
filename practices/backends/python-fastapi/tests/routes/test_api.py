from fastapi import status
from fastapi.testclient import TestClient


def test_heartbeat(test_client: TestClient) -> None:
    response = test_client.get("/api/heartbeat")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"alive": "1990-03-20T12:34:56.000789"}
