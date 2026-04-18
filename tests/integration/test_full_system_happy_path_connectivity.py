"""Happy-path integration slice for full-system service connectivity."""

import pytest

from ridenow_shared.testing.local_system import create_local_system


@pytest.mark.integration
def test_happy_path_traverses_the_real_service_graph() -> None:
    """Verify the local system can execute the happy path across all services."""

    system = create_local_system()

    result = system.run_happy_path()

    assert result.customer_statuses == [
        "request-submitted",
        "driver-assigned",
        "eta-updated",
        "payment-authorised",
        "trip-in-progress",
        "ride-completed",
        "payment-confirmed",
    ]
    assert result.services_touched == [
        "broker",
        "notification",
        "driver",
        "route",
        "pricing",
        "payment",
        "tracking",
        "notification",
        "broker",
    ]
