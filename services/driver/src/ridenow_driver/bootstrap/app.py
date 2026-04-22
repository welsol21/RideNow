"""Driver service composition root for startup/readiness wiring."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from ridenow_driver.core.application import (
    AssignDriverUseCase,
    EmitDriverLocationUpdateUseCase,
)
from ridenow_shared import create_probe_app, delayed_event_handler, run_service_app
from ridenow_shared.adapters import (
    RabbitMqEventConsumer,
    RabbitMqEventPublisher,
    create_event_consumer,
    create_event_publisher,
)
from ridenow_shared.config import SharedServiceSettings


@dataclass(frozen=True)
class DriverRuntime:
    """Real Driver runtime resources."""

    publisher: RabbitMqEventPublisher
    consumer: RabbitMqEventConsumer

    async def close(self) -> None:
        """Close all runtime resources owned by Driver."""

        await self.consumer.close()
        await self.publisher.close()


async def create_real_runtime(settings: SharedServiceSettings) -> DriverRuntime:
    """Create the RabbitMQ-backed Driver runtime."""

    publisher = await create_event_publisher(settings.rabbitmq)
    consumer = await create_event_consumer(settings.rabbitmq)
    assign_driver = AssignDriverUseCase(event_publisher=publisher)
    emit_location = EmitDriverLocationUpdateUseCase(event_publisher=publisher)

    await consumer.subscribe("DriverSearchRequested", assign_driver.execute)
    await consumer.subscribe(
        "PaymentAuthorised",
        delayed_event_handler(0.25, emit_location.execute),
    )
    return DriverRuntime(publisher=publisher, consumer=consumer)


def create_app() -> FastAPI:
    """Create the Driver FastAPI application."""

    runtime_mode = os.getenv("RIDENOW_RUNTIME_MODE", "local")
    if runtime_mode != "real":
        return create_probe_app("driver")

    settings = SharedServiceSettings(
        service_name=os.getenv("RIDENOW_SERVICE_NAME", "driver")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        runtime = await create_real_runtime(settings)
        yield
        await runtime.close()

    return create_probe_app("driver", lifespan=lifespan)


if __name__ == "__main__":
    run_service_app("ridenow_driver.bootstrap.app", "driver")
