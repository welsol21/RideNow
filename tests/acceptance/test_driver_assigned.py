"""Acceptance test for customer-visible driver assignment."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_driver_assignment_becomes_visible_to_the_customer(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that the customer can observe a driver-assigned ride state."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    response = broker_client.wait_for_status(ride_id, "driver-assigned")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "driver-assigned",
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
    }
