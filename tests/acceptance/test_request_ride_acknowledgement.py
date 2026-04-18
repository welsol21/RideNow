"""Acceptance test for ride request acknowledgement through the Broker."""

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_request_ride_returns_customer_visible_acknowledgement() -> None:
    """Verify that a passenger receives an acknowledgement after requesting a ride."""

    client = TestClient(create_app())

    response = client.post(
        "/rides",
        json={
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "ride_id": "ride-1",
        "status": "request-submitted",
    }
