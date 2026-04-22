"""Acceptance test for customer-visible payment authorisation."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_payment_authorisation_becomes_visible_to_the_customer(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that payment authorisation becomes visible after route feedback."""

    creation_response = broker_client.post(
        "/rides",
        {
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    eta_response = broker_client.wait_for_status(ride_id, "eta-updated")
    assert eta_response.status_code == 200
    assert eta_response.json()["status"] == "eta-updated"

    response = broker_client.wait_for_status(ride_id, "payment-authorised")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "payment-authorised",
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
    }
