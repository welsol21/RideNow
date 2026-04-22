"""Pricing service composition root for startup/readiness wiring."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from ridenow_pricing.core.application import CalculateFareUseCase
from ridenow_shared import create_probe_app, run_service_app
from ridenow_shared.adapters import (
    RabbitMqEventConsumer,
    RabbitMqEventPublisher,
    create_event_consumer,
    create_event_publisher,
)
from ridenow_shared.config import SharedServiceSettings


@dataclass(frozen=True)
class PricingRuntime:
    """Real Pricing runtime resources."""

    publisher: RabbitMqEventPublisher
    consumer: RabbitMqEventConsumer

    async def close(self) -> None:
        """Close all runtime resources owned by Pricing."""

        await self.consumer.close()
        await self.publisher.close()


async def create_real_runtime(settings: SharedServiceSettings) -> PricingRuntime:
    """Create the RabbitMQ-backed Pricing runtime."""

    publisher = await create_event_publisher(settings.rabbitmq)
    consumer = await create_event_consumer(settings.rabbitmq)
    calculate_fare = CalculateFareUseCase(event_publisher=publisher)
    await consumer.subscribe("FareRequested", calculate_fare.execute)
    return PricingRuntime(publisher=publisher, consumer=consumer)


def create_app() -> FastAPI:
    """Create the Pricing FastAPI application."""

    runtime_mode = os.getenv("RIDENOW_RUNTIME_MODE", "local")
    if runtime_mode != "real":
        return create_probe_app("pricing")

    settings = SharedServiceSettings(
        service_name=os.getenv("RIDENOW_SERVICE_NAME", "pricing")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        runtime = await create_real_runtime(settings)
        yield
        await runtime.close()

    return create_probe_app("pricing", lifespan=lifespan)


if __name__ == "__main__":
    run_service_app("ridenow_pricing.bootstrap.app", "pricing")
