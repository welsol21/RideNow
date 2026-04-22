"""Acceptance test for customer-visible no-driver-available outcome."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_no_driver_available_becomes_visible_to_the_customer(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that a missing-driver outcome becomes visible to the customer."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-no-driver",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    response = broker_client.wait_for_status(ride_id, "no-driver-available")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "no-driver-available",
    }
