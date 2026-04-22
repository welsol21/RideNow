"""Acceptance test for customer-visible trip progress."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_trip_progress_becomes_visible_to_the_customer(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that trip progress becomes visible after payment authorisation."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    payment_response = broker_client.wait_for_status(ride_id, "payment-authorised")
    assert payment_response.status_code == 200
    assert payment_response.json()["status"] == "payment-authorised"

    response = broker_client.wait_for_status(ride_id, "trip-in-progress")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "trip-in-progress",
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
        "route": {
            "distance_km": 4.8,
            "pickup_eta_minutes": 3,
            "trip_duration_minutes": 11,
        },
        "payment": {
            "authorisation_id": f"auth-{ride_id}",
            "amount": 18.5,
            "currency": "EUR",
        },
        "progress": {
            "phase": "driver-arriving",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    }
