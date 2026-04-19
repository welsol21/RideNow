"""HTTP adapter for Broker health and ride-request endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ridenow_broker.core.application.health import HealthCheckUseCase
from ridenow_broker.core.application.request_ride import (
    RequestRideCommand,
    RequestRideUseCase,
)
from ridenow_broker.core.application.issue_submission import (
    IssueSubmissionCommand,
    IssueSubmissionUseCase,
)
from ridenow_broker.core.application.ride_status import GetRideStatusUseCase


class CoordinatePayload(BaseModel):
    """Coordinate payload for request-ride HTTP input."""

    lat: float
    lon: float


class RequestRidePayload(BaseModel):
    """HTTP payload for creating a ride request."""

    customer_id: str
    pickup: CoordinatePayload
    dropoff: CoordinatePayload


class IssueSubmissionPayload(BaseModel):
    """HTTP payload for submitting a customer issue."""

    ride_id: str
    customer_id: str
    category: str
    description: str


class DriverPayload(BaseModel):
    """Customer-visible driver details."""

    driver_id: str
    vehicle_id: str


class RoutePayload(BaseModel):
    """Customer-visible route and ETA details."""

    distance_km: float
    pickup_eta_minutes: int
    trip_duration_minutes: int


class PaymentPayload(BaseModel):
    """Customer-visible payment authorisation details."""

    authorisation_id: str
    capture_id: str | None = None
    amount: float
    currency: str
    status: str | None = None


class ProgressPayload(BaseModel):
    """Customer-visible trip progress details."""

    phase: str
    driver_lat: float
    driver_lon: float


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


def create_ride_status_router(use_case: GetRideStatusUseCase) -> APIRouter:
    """Create the Broker router containing the customer-visible ride read endpoint."""

    router = APIRouter()

    @router.get("/rides/{ride_id}")
    async def get_ride_status(ride_id: str) -> dict[str, object]:
        """Return customer-visible ride state for the given ride identifier."""

        result = await use_case.execute(ride_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Ride not found")

        response: dict[str, object] = {
            "ride_id": result.ride_id,
            "status": result.status,
        }
        if result.driver is not None:
            response["driver"] = DriverPayload(**result.driver).model_dump()
        if result.route is not None:
            response["route"] = RoutePayload(**result.route).model_dump()
        if result.payment is not None:
            response["payment"] = PaymentPayload(**result.payment).model_dump(
                exclude_none=True
            )
        if result.progress is not None:
            response["progress"] = ProgressPayload(**result.progress).model_dump()
        return response

    return router


def create_issue_submission_router(use_case: IssueSubmissionUseCase) -> APIRouter:
    """Create the Broker router containing the issue-submission endpoint."""

    router = APIRouter()

    @router.post("/issues", status_code=202)
    async def submit_issue(payload: IssueSubmissionPayload) -> dict[str, str]:
        """Acknowledge a customer issue submission and return a traceable identifier."""

        result = await use_case.execute(
            IssueSubmissionCommand(
                ride_id=payload.ride_id,
                customer_id=payload.customer_id,
                category=payload.category,
                description=payload.description,
            )
        )
        return {
            "issue_id": result.issue_id,
            "status": result.status,
        }

    return router
