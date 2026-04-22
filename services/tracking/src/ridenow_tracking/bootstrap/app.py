"""Tracking service composition root for startup/readiness wiring."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from ridenow_shared import create_probe_app, delayed_event_handler, run_service_app
from ridenow_shared.adapters import (
    RabbitMqEventConsumer,
    RabbitMqEventPublisher,
    create_event_consumer,
    create_event_publisher,
)
from ridenow_shared.config import SharedServiceSettings
from ridenow_tracking.core.application import (
    CompleteTripUseCase,
    DeriveTripStatusUseCase,
)


@dataclass(frozen=True)
class TrackingRuntime:
    """Real Tracking runtime resources."""

    publisher: RabbitMqEventPublisher
    consumer: RabbitMqEventConsumer

    async def close(self) -> None:
        """Close all runtime resources owned by Tracking."""

        await self.consumer.close()
        await self.publisher.close()


async def create_real_runtime(settings: SharedServiceSettings) -> TrackingRuntime:
    """Create the RabbitMQ-backed Tracking runtime."""

    publisher = await create_event_publisher(settings.rabbitmq)
    consumer = await create_event_consumer(settings.rabbitmq)
    derive_trip_status = DeriveTripStatusUseCase(event_publisher=publisher)
    complete_trip = CompleteTripUseCase(event_publisher=publisher)

    await consumer.subscribe("TrackingLocationUpdated", derive_trip_status.execute)
    await consumer.subscribe(
        "TrackingLocationUpdated",
        delayed_event_handler(0.25, complete_trip.execute),
    )
    return TrackingRuntime(publisher=publisher, consumer=consumer)


def create_app() -> FastAPI:
    """Create the Tracking FastAPI application."""

    runtime_mode = os.getenv("RIDENOW_RUNTIME_MODE", "local")
    if runtime_mode != "real":
        return create_probe_app("tracking")

    settings = SharedServiceSettings(
        service_name=os.getenv("RIDENOW_SERVICE_NAME", "tracking")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        runtime = await create_real_runtime(settings)
        yield
        await runtime.close()

    return create_probe_app("tracking", lifespan=lifespan)


if __name__ == "__main__":
    run_service_app("ridenow_tracking.bootstrap.app", "tracking")
