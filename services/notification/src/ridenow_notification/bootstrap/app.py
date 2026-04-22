"""Notification service composition root for startup/readiness wiring."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from ridenow_notification.core.application import (
    RelayDriverSearchUseCase,
    RelayFareRequestUseCase,
    RelayNoDriverAvailableUseCase,
    RelayPaymentAuthorisationRequestUseCase,
    RelayPaymentCapturedUseCase,
    RelayPaymentFailedUseCase,
    RelayRouteRequestUseCase,
    RelayTrackingLocationUseCase,
    RelayTripCompletedUseCase,
    RelayTripStatusUseCase,
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
class NotificationRuntime:
    """Real Notification runtime resources."""

    publisher: RabbitMqEventPublisher
    consumer: RabbitMqEventConsumer

    async def close(self) -> None:
        """Close all runtime resources owned by Notification."""

        await self.consumer.close()
        await self.publisher.close()


async def create_real_runtime(settings: SharedServiceSettings) -> NotificationRuntime:
    """Create the RabbitMQ-backed Notification runtime."""

    publisher = await create_event_publisher(settings.rabbitmq)
    consumer = await create_event_consumer(settings.rabbitmq)
    relay_driver_search = RelayDriverSearchUseCase(event_publisher=publisher)
    relay_fare_request = RelayFareRequestUseCase(event_publisher=publisher)
    relay_no_driver_available = RelayNoDriverAvailableUseCase(event_publisher=publisher)
    relay_payment_authorisation = RelayPaymentAuthorisationRequestUseCase(
        event_publisher=publisher
    )
    relay_payment_captured = RelayPaymentCapturedUseCase(event_publisher=publisher)
    relay_payment_failed = RelayPaymentFailedUseCase(event_publisher=publisher)
    relay_route_request = RelayRouteRequestUseCase(event_publisher=publisher)
    relay_tracking_location = RelayTrackingLocationUseCase(event_publisher=publisher)
    relay_trip_completed = RelayTripCompletedUseCase(event_publisher=publisher)
    relay_trip_status = RelayTripStatusUseCase(event_publisher=publisher)

    await consumer.subscribe("RideRequested", relay_driver_search.execute)
    await consumer.subscribe(
        "NoDriverAvailable",
        relay_no_driver_available.execute,
    )
    await consumer.subscribe(
        "DriverAssigned",
        delayed_event_handler(0.25, relay_route_request.execute),
    )
    await consumer.subscribe(
        "EtaUpdated",
        delayed_event_handler(0.25, relay_fare_request.execute),
    )
    await consumer.subscribe("FareEstimated", relay_payment_authorisation.execute)
    await consumer.subscribe("PaymentFailed", relay_payment_failed.execute)
    await consumer.subscribe("DriverLocationUpdated", relay_tracking_location.execute)
    await consumer.subscribe("TripStatusUpdated", relay_trip_status.execute)
    await consumer.subscribe("TripCompleted", relay_trip_completed.execute)
    await consumer.subscribe("PaymentCaptured", relay_payment_captured.execute)
    return NotificationRuntime(publisher=publisher, consumer=consumer)


def create_app() -> FastAPI:
    """Create the Notification FastAPI application."""

    runtime_mode = os.getenv("RIDENOW_RUNTIME_MODE", "local")
    if runtime_mode != "real":
        return create_probe_app("notification")

    settings = SharedServiceSettings(
        service_name=os.getenv("RIDENOW_SERVICE_NAME", "notification")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        runtime = await create_real_runtime(settings)
        yield
        await runtime.close()

    return create_probe_app("notification", lifespan=lifespan)


if __name__ == "__main__":
    run_service_app("ridenow_notification.bootstrap.app", "notification")
