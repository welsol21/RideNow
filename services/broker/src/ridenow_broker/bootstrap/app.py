"""Broker service composition root for the walking skeleton."""

from fastapi import FastAPI

from ridenow_broker.adapters.health import StaticHealthCheckAdapter
from ridenow_broker.adapters.http import create_health_router
from ridenow_broker.core.application.health import HealthCheckUseCase


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
    use_case = HealthCheckUseCase(StaticHealthCheckAdapter(service_name="broker"))
    app.include_router(create_health_router(use_case))
    return app
