"""Payment service composition root for startup/readiness wiring."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from ridenow_payment.core.application import (
    AuthorisePaymentUseCase,
    CapturePaymentUseCase,
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
class PaymentRuntime:
    """Real Payment runtime resources."""

    publisher: RabbitMqEventPublisher
    consumer: RabbitMqEventConsumer

    async def close(self) -> None:
        """Close all runtime resources owned by Payment."""

        await self.consumer.close()
        await self.publisher.close()


async def create_real_runtime(settings: SharedServiceSettings) -> PaymentRuntime:
    """Create the RabbitMQ-backed Payment runtime."""

    publisher = await create_event_publisher(settings.rabbitmq)
    consumer = await create_event_consumer(settings.rabbitmq)
    authorise_payment = AuthorisePaymentUseCase(event_publisher=publisher)
    capture_payment = CapturePaymentUseCase(event_publisher=publisher)

    await consumer.subscribe("PaymentAuthorisationRequested", authorise_payment.execute)
    await consumer.subscribe(
        "PaymentCaptureRequested",
        delayed_event_handler(0.25, capture_payment.execute),
    )
    return PaymentRuntime(publisher=publisher, consumer=consumer)


def create_app() -> FastAPI:
    """Create the Payment FastAPI application."""

    runtime_mode = os.getenv("RIDENOW_RUNTIME_MODE", "local")
    if runtime_mode != "real":
        return create_probe_app("payment")

    settings = SharedServiceSettings(
        service_name=os.getenv("RIDENOW_SERVICE_NAME", "payment")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        runtime = await create_real_runtime(settings)
        yield
        await runtime.close()

    return create_probe_app("payment", lifespan=lifespan)


if __name__ == "__main__":
    run_service_app("ridenow_payment.bootstrap.app", "payment")
