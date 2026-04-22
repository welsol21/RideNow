"""Broker service composition root for the HTTP inbound adapter."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ridenow_broker.adapters.http import (
    create_health_router,
    create_issue_submission_router,
    create_request_ride_router,
    create_ride_status_router,
)
from ridenow_broker.bootstrap.real_runtime import create_real_runtime
from ridenow_broker.bootstrap.runtime import create_runtime
from ridenow_shared import (
    attach_metrics,
    attach_request_logging,
    configure_structured_logging,
    run_service_app,
)
from ridenow_shared.config import SharedServiceSettings


def create_app() -> FastAPI:
    """Create the Broker FastAPI application."""

    configure_structured_logging()
    app = FastAPI(title="RideNow Broker", version="0.1.0")
    runtime_mode = os.getenv("RIDENOW_RUNTIME_MODE", "local")
    if runtime_mode == "real":
        settings = SharedServiceSettings(
            service_name=os.getenv("RIDENOW_SERVICE_NAME", "broker")
        )

        @asynccontextmanager
        async def lifespan(_: FastAPI) -> AsyncIterator[None]:
            app.state.runtime = await create_real_runtime(settings)
            yield
            await app.state.runtime.close()

        app = FastAPI(title="RideNow Broker", version="0.1.0", lifespan=lifespan)
    else:
        app.state.runtime = create_runtime()
    app.include_router(create_health_router(lambda: app.state.runtime.health_check))
    app.include_router(
        create_request_ride_router(lambda: app.state.runtime.request_ride)
    )
    app.include_router(
        create_issue_submission_router(lambda: app.state.runtime.issue_submission)
    )
    app.include_router(create_ride_status_router(lambda: app.state.runtime.ride_status))
    attach_metrics(app, "broker")
    attach_request_logging(app, "broker")
    return app


if __name__ == "__main__":
    run_service_app("ridenow_broker.bootstrap.app", "broker")
