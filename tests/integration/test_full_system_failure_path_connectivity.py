"""Failure-path integration slice for full-system service connectivity."""

import pytest

from ridenow_shared.testing.local_system import create_local_system


@pytest.mark.integration
@pytest.mark.parametrize(
    ("failure_mode", "expected_statuses", "expected_services"),
    [
        (
            "no-driver-available",
            ["request-submitted", "no-driver-available"],
            ["broker", "notification", "driver", "notification", "broker"],
        ),
        (
            "payment-failed",
            ["request-submitted", "driver-assigned", "payment-failed"],
            [
                "broker",
                "notification",
                "driver",
                "route",
                "pricing",
                "payment",
                "notification",
                "broker",
            ],
        ),
    ],
)
def test_failure_paths_traverse_the_real_service_graph(
    failure_mode: str,
    expected_statuses: list[str],
    expected_services: list[str],
) -> None:
    """Verify principal failure modes flow through the full service graph."""

    system = create_local_system()

    result = system.run_failure_path(failure_mode)

    assert result.customer_statuses == expected_statuses
    assert result.services_touched == expected_services
