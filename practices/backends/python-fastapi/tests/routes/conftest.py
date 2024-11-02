from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture

from src.main import app


@pytest.fixture
def test_client(
    mocker: MockFixture,
) -> TestClient:
    mock_datetime = mocker.patch("src.routes.api.datetime")
    mock_datetime.now.return_value = datetime(1990, 3, 20, 12, 34, 56, 789)

    return TestClient(app)
