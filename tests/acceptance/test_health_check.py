"""Acceptance test for the initial walking skeleton health endpoint."""

import pytest
from fastapi.testclient import TestClient
from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_health_check_returns_ok() -> None:
    """Verify that the broker health endpoint returns the expected payload."""

    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "broker",
        "status": "ok",
    }
