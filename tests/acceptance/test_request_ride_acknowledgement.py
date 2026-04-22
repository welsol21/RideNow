"""Acceptance test for ride request acknowledgement through the Broker."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_request_ride_returns_customer_visible_acknowledgement(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that a passenger receives an acknowledgement after requesting a ride."""

    response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "request-submitted"
    assert str(payload["ride_id"]).startswith("ride-")
