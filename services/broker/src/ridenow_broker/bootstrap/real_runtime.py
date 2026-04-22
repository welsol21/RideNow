"""Real Broker runtime wiring backed by RabbitMQ and PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import TYPE_CHECKING

from ridenow_broker.adapters.health import StaticHealthCheckAdapter
from ridenow_broker.core.application import (
    ApplyDriverAssignedUseCase,
    ApplyEtaUpdatedUseCase,
    ApplyNoDriverAvailableUseCase,
    ApplyPaymentAuthorisedUseCase,
    ApplyPaymentConfirmedUseCase,
    ApplyPaymentFailedUseCase,
    ApplyRideCompletedUseCase,
    ApplyTripProgressUseCase,
    GetRideStatusUseCase,
    HealthCheckUseCase,
    IssueSubmissionUseCase,
    RequestRideUseCase,
)
from ridenow_shared.adapters import (
    PostgresStateStore,
    RabbitMqEventConsumer,
    RabbitMqEventPublisher,
    create_event_consumer,
    create_event_publisher,
    create_state_store,
)

if TYPE_CHECKING:
    from ridenow_shared.config import SharedServiceSettings


@dataclass(frozen=True)
class RealBrokerRuntime:
    """Runtime object exposing Broker use cases and owned resources."""

    health_check: HealthCheckUseCase
    request_ride: RequestRideUseCase
    issue_submission: IssueSubmissionUseCase
    ride_status: GetRideStatusUseCase
    _publisher: RabbitMqEventPublisher
    _consumer: RabbitMqEventConsumer
    _ride_status_store: PostgresStateStore
    _issue_store: PostgresStateStore

    async def close(self) -> None:
        """Close all runtime resources owned by the Broker."""

        await self._consumer.close()
        await self._publisher.close()
        await self._issue_store.close()
        await self._ride_status_store.close()


async def create_real_runtime(settings: SharedServiceSettings) -> RealBrokerRuntime:
    """Create the RabbitMQ/PostgreSQL-backed Broker runtime."""

    publisher = await create_event_publisher(settings.rabbitmq)
    consumer = await create_event_consumer(settings.rabbitmq)
    ride_status_store = await create_state_store(
        store_name="broker-ride-status",
        settings=settings.postgres,
    )
    issue_store = await create_state_store(
        store_name="broker-issue-store",
        settings=settings.postgres,
    )

    health_check = HealthCheckUseCase(
        StaticHealthCheckAdapter(service_name=settings.service_name)
    )
    ride_sequence = count(1)
    issue_sequence = count(1)

    request_ride = RequestRideUseCase(
        status_store=ride_status_store,
        event_publisher=publisher,
        ride_id_factory=lambda: f"ride-{next(ride_sequence)}",
    )
    issue_submission = IssueSubmissionUseCase(
        issue_store=issue_store,
        event_publisher=publisher,
        issue_id_factory=lambda: f"issue-{next(issue_sequence)}",
    )
    ride_status = GetRideStatusUseCase(status_store=ride_status_store)

    apply_driver_assigned = ApplyDriverAssignedUseCase(status_store=ride_status_store)
    apply_eta_updated = ApplyEtaUpdatedUseCase(status_store=ride_status_store)
    apply_no_driver_available = ApplyNoDriverAvailableUseCase(
        status_store=ride_status_store
    )
    apply_payment_failed = ApplyPaymentFailedUseCase(status_store=ride_status_store)
    apply_payment_authorised = ApplyPaymentAuthorisedUseCase(
        status_store=ride_status_store
    )
    apply_payment_confirmed = ApplyPaymentConfirmedUseCase(
        status_store=ride_status_store
    )
    apply_ride_completed = ApplyRideCompletedUseCase(status_store=ride_status_store)
    apply_trip_progress = ApplyTripProgressUseCase(status_store=ride_status_store)

    await consumer.subscribe("DriverAssigned", apply_driver_assigned.execute)
    await consumer.subscribe("EtaUpdated", apply_eta_updated.execute)
    await consumer.subscribe(
        "NoDriverAvailableVisible",
        apply_no_driver_available.execute,
    )
    await consumer.subscribe("PaymentFailedVisible", apply_payment_failed.execute)
    await consumer.subscribe("PaymentAuthorised", apply_payment_authorised.execute)
    await consumer.subscribe("PaymentConfirmedVisible", apply_payment_confirmed.execute)
    await consumer.subscribe("RideCompletedVisible", apply_ride_completed.execute)
    await consumer.subscribe("TripProgressVisible", apply_trip_progress.execute)

    return RealBrokerRuntime(
        health_check=health_check,
        request_ride=request_ride,
        issue_submission=issue_submission,
        ride_status=ride_status,
        _publisher=publisher,
        _consumer=consumer,
        _ride_status_store=ride_status_store,
        _issue_store=issue_store,
    )
