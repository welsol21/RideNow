"""Broker service composition root for the walking skeleton."""

import asyncio
from threading import Timer

from fastapi import FastAPI

from ridenow_broker.adapters.http import create_request_ride_router
from ridenow_broker.adapters.health import StaticHealthCheckAdapter
from ridenow_broker.adapters.http import create_health_router, create_ride_status_router
from ridenow_broker.core.application.apply_driver_assigned import (
    ApplyDriverAssignedUseCase,
)
from ridenow_broker.core.application.apply_eta_updated import ApplyEtaUpdatedUseCase
from ridenow_broker.core.application.apply_payment_authorised import (
    ApplyPaymentAuthorisedUseCase,
)
from ridenow_broker.core.application.apply_payment_confirmed import (
    ApplyPaymentConfirmedUseCase,
)
from ridenow_broker.core.application.apply_ride_completed import (
    ApplyRideCompletedUseCase,
)
from ridenow_broker.core.application.apply_trip_progress import ApplyTripProgressUseCase
from ridenow_broker.core.application.health import HealthCheckUseCase
from ridenow_broker.core.application.request_ride import RequestRideUseCase
from ridenow_broker.core.application.ride_status import GetRideStatusUseCase
from ridenow_driver.core.application.assign_driver import AssignDriverUseCase
from ridenow_driver.core.application.emit_driver_location_update import (
    EmitDriverLocationUpdateUseCase,
)
from ridenow_notification.core.application.relay_driver_search import (
    RelayDriverSearchUseCase,
)
from ridenow_notification.core.application.relay_fare_request import (
    RelayFareRequestUseCase,
)
from ridenow_notification.core.application.relay_payment_captured import (
    RelayPaymentCapturedUseCase,
)
from ridenow_notification.core.application.relay_payment_authorisation_request import (
    RelayPaymentAuthorisationRequestUseCase,
)
from ridenow_notification.core.application.relay_tracking_location import (
    RelayTrackingLocationUseCase,
)
from ridenow_notification.core.application.relay_trip_completed import (
    RelayTripCompletedUseCase,
)
from ridenow_notification.core.application.relay_trip_status import (
    RelayTripStatusUseCase,
)
from ridenow_notification.core.application.relay_route_request import (
    RelayRouteRequestUseCase,
)
from ridenow_payment.core.application.authorise_payment import AuthorisePaymentUseCase
from ridenow_payment.core.application.capture_payment import CapturePaymentUseCase
from ridenow_pricing.core.application.calculate_fare import CalculateFareUseCase
from ridenow_route.core.application.calculate_route import CalculateRouteUseCase
from ridenow_shared.adapters.in_memory import InMemoryEventBus, InMemoryStateStore
from ridenow_tracking.core.application.derive_trip_status import DeriveTripStatusUseCase
from ridenow_tracking.core.application.complete_trip import CompleteTripUseCase


def create_app() -> FastAPI:
    """Create the Broker FastAPI application.

    Parameters:
        None.
    Return value:
        Configured FastAPI application for the Broker service.
    Exceptions raised:
        RuntimeError: Propagated from application wiring dependencies if they fail.
    Example:
        app = create_app()
    """

    app = FastAPI(title="RideNow Broker", version="0.1.0")
    health_use_case = HealthCheckUseCase(StaticHealthCheckAdapter(service_name="broker"))
    status_store = InMemoryStateStore[dict[str, object]]()
    event_bus = InMemoryEventBus()
    request_ride_use_case = RequestRideUseCase(
        status_store=status_store,
        event_publisher=event_bus,
    )
    ride_status_use_case = GetRideStatusUseCase(status_store=status_store)
    notification_relay_use_case = RelayDriverSearchUseCase(event_publisher=event_bus)
    fare_request_relay_use_case = RelayFareRequestUseCase(event_publisher=event_bus)
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
    apply_driver_assigned_use_case = ApplyDriverAssignedUseCase(status_store=status_store)
    apply_eta_updated_use_case = ApplyEtaUpdatedUseCase(status_store=status_store)
    apply_payment_authorised_use_case = ApplyPaymentAuthorisedUseCase(
        status_store=status_store
    )
    apply_payment_confirmed_use_case = ApplyPaymentConfirmedUseCase(
        status_store=status_store
    )
    apply_ride_completed_use_case = ApplyRideCompletedUseCase(status_store=status_store)
    apply_trip_progress_use_case = ApplyTripProgressUseCase(status_store=status_store)

    async def schedule_route_request(event) -> None:
        """Delay route processing so driver assignment remains the first visible state."""

        Timer(
            0.1,
            lambda: asyncio.run(route_request_relay_use_case.execute(event)),
        ).start()

    async def schedule_fare_request(event) -> None:
        """Delay fare processing so ETA feedback remains visible first."""

        Timer(
            0.1,
            lambda: asyncio.run(fare_request_relay_use_case.execute(event)),
        ).start()

    async def schedule_driver_location_update(event) -> None:
        """Delay live-progress updates so payment authorisation remains visible first."""

        Timer(
            0.1,
            lambda: asyncio.run(emit_driver_location_update_use_case.execute(event)),
        ).start()

    async def schedule_trip_completed(event) -> None:
        """Delay trip completion so trip progress remains visible first."""

        Timer(
            0.1,
            lambda: asyncio.run(complete_trip_use_case.execute(event)),
        ).start()

    async def schedule_payment_capture(event) -> None:
        """Delay payment capture so ride completion remains visible first."""

        Timer(
            0.1,
            lambda: asyncio.run(capture_payment_use_case.execute(event)),
        ).start()

    asyncio.run(event_bus.subscribe("RideRequested", notification_relay_use_case.execute))
    asyncio.run(
        event_bus.subscribe("DriverSearchRequested", assign_driver_use_case.execute)
    )
    asyncio.run(event_bus.subscribe("DriverAssigned", apply_driver_assigned_use_case.execute))
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
        event_bus.subscribe("PaymentAuthorised", apply_payment_authorised_use_case.execute)
    )
    asyncio.run(event_bus.subscribe("PaymentAuthorised", schedule_driver_location_update))
    asyncio.run(
        event_bus.subscribe("DriverLocationUpdated", tracking_location_relay_use_case.execute)
    )
    asyncio.run(
        event_bus.subscribe("TrackingLocationUpdated", derive_trip_status_use_case.execute)
    )
    asyncio.run(event_bus.subscribe("TrackingLocationUpdated", schedule_trip_completed))
    asyncio.run(event_bus.subscribe("TripStatusUpdated", trip_status_relay_use_case.execute))
    asyncio.run(
        event_bus.subscribe("TripProgressVisible", apply_trip_progress_use_case.execute)
    )
    asyncio.run(event_bus.subscribe("TripCompleted", trip_completed_relay_use_case.execute))
    asyncio.run(
        event_bus.subscribe("RideCompletedVisible", apply_ride_completed_use_case.execute)
    )
    asyncio.run(event_bus.subscribe("PaymentCaptureRequested", schedule_payment_capture))
    asyncio.run(event_bus.subscribe("PaymentCaptured", payment_captured_relay_use_case.execute))
    asyncio.run(
        event_bus.subscribe(
            "PaymentConfirmedVisible",
            apply_payment_confirmed_use_case.execute,
        )
    )

    app.include_router(create_health_router(health_use_case))
    app.include_router(create_request_ride_router(request_ride_use_case))
    app.include_router(create_ride_status_router(ride_status_use_case))
    return app
