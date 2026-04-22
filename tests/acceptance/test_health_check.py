"""Acceptance test for the initial walking skeleton health endpoint."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_health_check_returns_ok(broker_client: BrokerAcceptanceClient) -> None:
    """Verify that the broker health endpoint returns the expected payload."""

    response = broker_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "broker",
        "status": "ok",
    }
