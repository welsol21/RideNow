"""Unit tests for the broker health check use case."""

from ridenow_broker.core.application.health import (
    HealthCheckUseCase,
    HealthStatus,
)


class HealthCheckPortStub:
    """Simple in-memory stub used to drive the health use case test."""

    def __init__(self, status: HealthStatus) -> None:
        """Store the health status returned by the stub."""

        self._status = status

    def get_status(self) -> HealthStatus:
        """Return the preconfigured health status."""

        return self._status


def test_health_check_use_case_returns_status_from_port() -> None:
    """Verify that the use case delegates to the configured port."""

    expected = HealthStatus(service="broker", status="ok")

    use_case = HealthCheckUseCase(HealthCheckPortStub(expected))

    assert use_case.execute() == expected
