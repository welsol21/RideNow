"""HTTP adapter for the Broker health check endpoint."""

from fastapi import APIRouter

from ridenow_broker.core.application.health import HealthCheckUseCase


def create_health_router(use_case: HealthCheckUseCase) -> APIRouter:
    """Create the Broker router containing the health endpoint.

    Parameters:
        use_case: Health check use case invoked by the route handler.
    Return value:
        Configured FastAPI router.
    Exceptions raised:
        RuntimeError: Propagated from the use case implementation if it fails.
    Example:
        router = create_health_router(use_case)
    """

    router = APIRouter()

    @router.get("/health")
    def health_check() -> dict[str, str]:
        """Return the current broker health payload."""

        status = use_case.execute()
        return {
            "service": status.service,
            "status": status.status,
        }

    return router
