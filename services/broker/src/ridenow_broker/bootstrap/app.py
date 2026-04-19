"""Broker service composition root for the HTTP inbound adapter."""

from fastapi import FastAPI

from ridenow_broker.adapters.http import (
    create_health_router,
    create_issue_submission_router,
    create_request_ride_router,
    create_ride_status_router,
)
from ridenow_broker.bootstrap.runtime import create_runtime


def create_app() -> FastAPI:
    """Create the Broker FastAPI application."""

    runtime = create_runtime()
    app = FastAPI(title="RideNow Broker", version="0.1.0")
    app.include_router(create_health_router(runtime.health_check))
    app.include_router(create_request_ride_router(runtime.request_ride))
    app.include_router(create_issue_submission_router(runtime.issue_submission))
    app.include_router(create_ride_status_router(runtime.ride_status))
    return app
