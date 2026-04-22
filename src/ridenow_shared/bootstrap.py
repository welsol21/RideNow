"""Shared bootstrap helpers for simple service composition roots."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

import uvicorn
from fastapi import FastAPI

from ridenow_shared.config import SharedServiceSettings
from ridenow_shared.logging import attach_request_logging, configure_structured_logging
from ridenow_shared.metrics import attach_metrics

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.types import Lifespan

    from ridenow_shared.events import EventEnvelope


def create_probe_app(
    service_name: str,
    *,
    lifespan: Lifespan[FastAPI] | None = None,
) -> FastAPI:
    """Create a minimal FastAPI app exposing health and readiness probes.

    Parameters:
        service_name: Logical name of the service application.
    Return value:
        Configured FastAPI application exposing `/health` and `/ready`.
    Exceptions raised:
        None.
    Example:
        app = create_probe_app("driver")
    """

    app = FastAPI(
        title=f"RideNow {service_name.title()}",
        version="0.1.0",
        lifespan=lifespan,
    )
    configure_structured_logging()
    attach_metrics(app, service_name)
    attach_request_logging(app, service_name)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        """Return the health probe payload."""

        return {
            "service": service_name,
            "status": "ok",
        }

    @app.get("/ready")
    def readiness_check() -> dict[str, str]:
        """Return the readiness probe payload."""

        return {
            "service": service_name,
            "status": "ready",
        }

    return app


def delayed_event_handler(
    delay_seconds: float,
    handler: Callable[[EventEnvelope], Awaitable[None]],
) -> Callable[[EventEnvelope], Awaitable[None]]:
    """Wrap an event handler with a small async delay."""

    async def delayed(event: EventEnvelope) -> None:
        await asyncio.sleep(delay_seconds)
        await handler(event)

    return delayed


def run_service_app(module_path: str, default_service_name: str) -> None:
    """Run a FastAPI app module using shared HTTP settings."""

    settings = SharedServiceSettings(
        service_name=os.getenv("RIDENOW_SERVICE_NAME", default_service_name)
    )
    uvicorn.run(
        f"{module_path}:create_app",
        factory=True,
        host=settings.http.host,
        port=settings.http.port,
        log_level=settings.http.log_level,
        access_log=False,
    )
