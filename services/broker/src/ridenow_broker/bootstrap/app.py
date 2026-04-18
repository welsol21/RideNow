"""Broker service composition root for the walking skeleton."""

from fastapi import FastAPI

from ridenow_broker.adapters.http import create_request_ride_router
from ridenow_broker.adapters.health import StaticHealthCheckAdapter
from ridenow_broker.adapters.http import create_health_router
from ridenow_broker.core.application.health import HealthCheckUseCase
from ridenow_broker.core.application.request_ride import RequestRideUseCase
from ridenow_shared.adapters.in_memory import InMemoryEventPublisher, InMemoryStateStore


def create_app() -> FastAPI:
    """Create the Broker FastAPI application.

    Parameters:
        None.
    Return value:
        Configured FastAPI application for the Broker service.
    Exceptions raised:
        RuntimeError: Propagated from application wiring dependencies if they fail.
    Example:
        app = create_app()
    """

    app = FastAPI(title="RideNow Broker", version="0.1.0")
    health_use_case = HealthCheckUseCase(StaticHealthCheckAdapter(service_name="broker"))
    request_ride_use_case = RequestRideUseCase(
        status_store=InMemoryStateStore(),
        event_publisher=InMemoryEventPublisher([]),
    )
    app.include_router(create_health_router(health_use_case))
    app.include_router(create_request_ride_router(request_ride_use_case))
    return app
