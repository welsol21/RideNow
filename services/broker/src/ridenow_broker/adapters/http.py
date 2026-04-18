"""HTTP adapter for Broker health and ride-request endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from ridenow_broker.core.application.health import HealthCheckUseCase
from ridenow_broker.core.application.request_ride import (
    RequestRideCommand,
    RequestRideUseCase,
)


class CoordinatePayload(BaseModel):
    """Coordinate payload for request-ride HTTP input."""

    lat: float
    lon: float


class RequestRidePayload(BaseModel):
    """HTTP payload for creating a ride request."""

    customer_id: str
    pickup: CoordinatePayload
    dropoff: CoordinatePayload


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

    @router.get("/ready")
    def readiness_check() -> dict[str, str]:
        """Return the current broker readiness payload."""

        status = use_case.execute()
        return {
            "service": status.service,
            "status": "ready",
        }

    return router


def create_request_ride_router(use_case: RequestRideUseCase) -> APIRouter:
    """Create the Broker router containing the ride-request endpoint."""

    router = APIRouter()

    @router.post("/rides", status_code=202)
    async def request_ride(payload: RequestRidePayload) -> dict[str, str]:
        """Acknowledge a ride request and return customer-visible status."""

        result = await use_case.execute(
            RequestRideCommand(
                customer_id=payload.customer_id,
                pickup=payload.pickup.model_dump(),
                dropoff=payload.dropoff.model_dump(),
            )
        )
        return {
            "ride_id": result.ride_id,
            "status": result.status,
        }

    return router
