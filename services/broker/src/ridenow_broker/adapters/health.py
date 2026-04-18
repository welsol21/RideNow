"""Outbound stub adapter for the Broker health check use case."""

from ridenow_broker.core.application.health import HealthCheckPort, HealthStatus


class StaticHealthCheckAdapter(HealthCheckPort):
    """Static adapter returning a fixed healthy status.

    Parameters:
        service_name: Logical service name to expose in the response.
    Return value:
        Adapter instance compatible with `HealthCheckPort`.
    Exceptions raised:
        None.
    Example:
        adapter = StaticHealthCheckAdapter(service_name="broker")
    """

    def __init__(self, service_name: str) -> None:
        """Store the service name used in the health payload."""

        self._service_name = service_name

    def get_status(self) -> HealthStatus:
        """Return a static healthy status for the configured service."""

        return HealthStatus(service=self._service_name, status="ok")
