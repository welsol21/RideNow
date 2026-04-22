"""Acceptance test for customer-visible route and ETA feedback."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_route_and_eta_feedback_become_visible_to_the_customer(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that route and ETA details become visible after driver assignment."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    first_status = broker_client.wait_for_status(ride_id, "driver-assigned")

    assert first_status.status_code == 200
    assert first_status.json()["status"] == "driver-assigned"

    response = broker_client.wait_for_status(ride_id, "eta-updated")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "eta-updated",
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
        "route": {
            "distance_km": 4.8,
            "pickup_eta_minutes": 3,
            "trip_duration_minutes": 11,
        },
    }
