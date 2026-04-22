"""Acceptance test for ride completion and payment confirmation."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_ride_completion_and_payment_confirmation_become_visible(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that ride completion and payment confirmation become customer-visible."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    progress_response = broker_client.wait_for_status(ride_id, "trip-in-progress")
    assert progress_response.status_code == 200
    assert progress_response.json()["status"] == "trip-in-progress"

    completed_response = broker_client.wait_for_status(ride_id, "ride-completed")

    assert completed_response.status_code == 200
    assert completed_response.json()["status"] == "ride-completed"

    response = broker_client.wait_for_status(ride_id, "payment-confirmed")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "payment-confirmed",
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
            "capture_id": f"cap-{ride_id}",
            "amount": 18.5,
            "currency": "EUR",
            "status": "captured",
        },
        "progress": {
            "phase": "ride-completed",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    }
