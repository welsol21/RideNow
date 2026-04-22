"""Acceptance test for customer-visible payment failure."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_payment_failed_becomes_visible_to_the_customer(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that a payment failure becomes visible to the customer."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-payment-fail",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    response = broker_client.wait_for_status(ride_id, "payment-failed")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "payment-failed",
    }
