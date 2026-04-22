"""Shared Broker runtime wiring reused by HTTP and CLI adapters."""

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from threading import Timer

from ridenow_driver.core.application import (
    AssignDriverUseCase,
    EmitDriverLocationUpdateUseCase,
)
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
from ridenow_payment.core.application import (
    AuthorisePaymentUseCase,
    CapturePaymentUseCase,
)
from ridenow_pricing.core.application import CalculateFareUseCase
from ridenow_route.core.application import CalculateRouteUseCase
from ridenow_tracking.core.application import (
    CompleteTripUseCase,
    DeriveTripStatusUseCase,
)

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
from ridenow_shared.adapters.in_memory import InMemoryEventBus, InMemoryStateStore
from ridenow_shared.events import EventEnvelope


@dataclass(frozen=True)
class BrokerRuntime:
    """Runtime object exposing Broker inbound-use-case entry points."""

    health_check: HealthCheckUseCase
    request_ride: RequestRideUseCase
    issue_submission: IssueSubmissionUseCase
    ride_status: GetRideStatusUseCase


def create_runtime() -> BrokerRuntime:
    """Create the in-memory Broker runtime used by local adapters."""

    health_use_case = HealthCheckUseCase(
        StaticHealthCheckAdapter(service_name="broker")
    )
    status_store = InMemoryStateStore[dict[str, object]]()
    event_bus = InMemoryEventBus()
    issue_store = InMemoryStateStore[dict[str, object]]()
    request_ride_use_case = RequestRideUseCase(
        status_store=status_store,
        event_publisher=event_bus,
    )
    issue_submission_use_case = IssueSubmissionUseCase(
        issue_store=issue_store,
        event_publisher=event_bus,
    )
    ride_status_use_case = GetRideStatusUseCase(status_store=status_store)
    notification_relay_use_case = RelayDriverSearchUseCase(event_publisher=event_bus)
    fare_request_relay_use_case = RelayFareRequestUseCase(event_publisher=event_bus)
    no_driver_available_relay_use_case = RelayNoDriverAvailableUseCase(
        event_publisher=event_bus
    )
    payment_failed_relay_use_case = RelayPaymentFailedUseCase(event_publisher=event_bus)
    payment_authorisation_request_relay_use_case = (
        RelayPaymentAuthorisationRequestUseCase(event_publisher=event_bus)
    )
    payment_captured_relay_use_case = RelayPaymentCapturedUseCase(
        event_publisher=event_bus
    )
    tracking_location_relay_use_case = RelayTrackingLocationUseCase(
        event_publisher=event_bus
    )
    trip_completed_relay_use_case = RelayTripCompletedUseCase(event_publisher=event_bus)
    trip_status_relay_use_case = RelayTripStatusUseCase(event_publisher=event_bus)
    route_request_relay_use_case = RelayRouteRequestUseCase(event_publisher=event_bus)
    assign_driver_use_case = AssignDriverUseCase(event_publisher=event_bus)
    emit_driver_location_update_use_case = EmitDriverLocationUpdateUseCase(
        event_publisher=event_bus
    )
    calculate_fare_use_case = CalculateFareUseCase(event_publisher=event_bus)
    authorise_payment_use_case = AuthorisePaymentUseCase(event_publisher=event_bus)
    capture_payment_use_case = CapturePaymentUseCase(event_publisher=event_bus)
    calculate_route_use_case = CalculateRouteUseCase(event_publisher=event_bus)
    complete_trip_use_case = CompleteTripUseCase(event_publisher=event_bus)
    derive_trip_status_use_case = DeriveTripStatusUseCase(event_publisher=event_bus)
    apply_driver_assigned_use_case = ApplyDriverAssignedUseCase(
        status_store=status_store
    )
    apply_eta_updated_use_case = ApplyEtaUpdatedUseCase(status_store=status_store)
    apply_no_driver_available_use_case = ApplyNoDriverAvailableUseCase(
        status_store=status_store
    )
    apply_payment_failed_use_case = ApplyPaymentFailedUseCase(status_store=status_store)
    apply_payment_authorised_use_case = ApplyPaymentAuthorisedUseCase(
        status_store=status_store
    )
    apply_payment_confirmed_use_case = ApplyPaymentConfirmedUseCase(
        status_store=status_store
    )
    apply_ride_completed_use_case = ApplyRideCompletedUseCase(status_store=status_store)
    apply_trip_progress_use_case = ApplyTripProgressUseCase(status_store=status_store)

    def _schedule(
        delay_seconds: float,
        handler: Callable[[EventEnvelope], Coroutine[object, object, None]],
    ) -> Callable[[EventEnvelope], Coroutine[object, object, None]]:
        async def delayed_handler(event: EventEnvelope) -> None:
            Timer(delay_seconds, lambda: asyncio.run(handler(event))).start()

        return delayed_handler

    transition_delay_seconds = 0.25

    schedule_route_request = _schedule(
        transition_delay_seconds,
        route_request_relay_use_case.execute,
    )
    schedule_fare_request = _schedule(
        transition_delay_seconds,
        fare_request_relay_use_case.execute,
    )
    schedule_driver_location_update = _schedule(
        transition_delay_seconds,
        emit_driver_location_update_use_case.execute,
    )
    schedule_trip_completed = _schedule(
        transition_delay_seconds,
        complete_trip_use_case.execute,
    )
    schedule_payment_capture = _schedule(
        transition_delay_seconds,
        capture_payment_use_case.execute,
    )

    asyncio.run(
        event_bus.subscribe("RideRequested", notification_relay_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe("DriverSearchRequested", assign_driver_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe(
            "NoDriverAvailable",
            no_driver_available_relay_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe(
            "DriverAssigned",
            apply_driver_assigned_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe(
            "NoDriverAvailableVisible",
            apply_no_driver_available_use_case.execute,
        )
    )
    asyncio.run(event_bus.subscribe("DriverAssigned", schedule_route_request))
    asyncio.run(event_bus.subscribe("RouteRequested", calculate_route_use_case.execute))
    asyncio.run(event_bus.subscribe("EtaUpdated", apply_eta_updated_use_case.execute))
    asyncio.run(event_bus.subscribe("EtaUpdated", schedule_fare_request))
    asyncio.run(event_bus.subscribe("FareRequested", calculate_fare_use_case.execute))
    asyncio.run(
        event_bus.subscribe(
            "FareEstimated",
            payment_authorisation_request_relay_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe(
            "PaymentAuthorisationRequested",
            authorise_payment_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe("PaymentFailed", payment_failed_relay_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe(
            "PaymentAuthorised",
            apply_payment_authorised_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe(
            "PaymentFailedVisible",
            apply_payment_failed_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe("PaymentAuthorised", schedule_driver_location_update)
    )
    asyncio.run(
        event_bus.subscribe(
            "DriverLocationUpdated",
            tracking_location_relay_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe(
            "TrackingLocationUpdated",
            derive_trip_status_use_case.execute,
        )
    )
    asyncio.run(event_bus.subscribe("TrackingLocationUpdated", schedule_trip_completed))
    asyncio.run(
        event_bus.subscribe("TripStatusUpdated", trip_status_relay_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe("TripProgressVisible", apply_trip_progress_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe("TripCompleted", trip_completed_relay_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe(
            "RideCompletedVisible",
            apply_ride_completed_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe("PaymentCaptureRequested", schedule_payment_capture)
    )
    asyncio.run(
        event_bus.subscribe(
            "PaymentCaptured",
            payment_captured_relay_use_case.execute,
        )
    )
    asyncio.run(
        event_bus.subscribe(
            "PaymentConfirmedVisible",
            apply_payment_confirmed_use_case.execute,
        )
    )

    return BrokerRuntime(
        health_check=health_use_case,
        request_ride=request_ride_use_case,
        issue_submission=issue_submission_use_case,
        ride_status=ride_status_use_case,
    )
