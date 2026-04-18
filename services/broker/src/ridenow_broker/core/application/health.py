"""Application-layer health check use case for the Broker service."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HealthStatus:
    """Health status DTO for service liveness.

    Parameters:
        service: Logical service name.
        status: Reported service status.
    Return value:
        Immutable health status value returned by the use case.
    Exceptions raised:
        None.
    Example:
        HealthStatus(service="broker", status="ok")
    """

    service: str
    status: str


class HealthCheckPort(Protocol):
    """Outbound port that supplies the current health state.

    Parameters:
        None.
    Return value:
        `HealthStatus` describing the service state.
    Exceptions raised:
        Implementation-specific exceptions may propagate.
    Example:
        status = port.get_status()
    """

    def get_status(self) -> HealthStatus:
        """Return the current health status."""


class HealthCheckUseCase:
    """Use case that retrieves the current service health.

    Parameters:
        port: Health state provider used by the application layer.
    Return value:
        Instance capable of retrieving a health status report.
    Exceptions raised:
        Implementation-specific exceptions may propagate from the port.
    Example:
        report = HealthCheckUseCase(port).execute()
    """

    def __init__(self, port: HealthCheckPort) -> None:
        """Store the outbound health-check dependency."""

        self._port = port

    def execute(self) -> HealthStatus:
        """Return the health status from the configured port."""

        return self._port.get_status()
