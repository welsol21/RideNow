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
from ridenow_broker.core.application.health import HealthCheckUseCase
from ridenow_broker.core.application.request_ride import RequestRideUseCase
from ridenow_broker.core.application.ride_status import GetRideStatusUseCase
from ridenow_driver.core.application.assign_driver import AssignDriverUseCase
from ridenow_notification.core.application.relay_driver_search import (
    RelayDriverSearchUseCase,
)
from ridenow_notification.core.application.relay_route_request import (
    RelayRouteRequestUseCase,
)
from ridenow_route.core.application.calculate_route import CalculateRouteUseCase
from ridenow_shared.adapters.in_memory import InMemoryEventBus, InMemoryStateStore


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
    route_request_relay_use_case = RelayRouteRequestUseCase(event_publisher=event_bus)
    assign_driver_use_case = AssignDriverUseCase(event_publisher=event_bus)
    calculate_route_use_case = CalculateRouteUseCase(event_publisher=event_bus)
    apply_driver_assigned_use_case = ApplyDriverAssignedUseCase(status_store=status_store)
    apply_eta_updated_use_case = ApplyEtaUpdatedUseCase(status_store=status_store)

    async def schedule_route_request(event) -> None:
        """Delay route processing so driver assignment remains the first visible state."""

        Timer(
            0.1,
            lambda: asyncio.run(route_request_relay_use_case.execute(event)),
        ).start()

    asyncio.run(event_bus.subscribe("RideRequested", notification_relay_use_case.execute))
    asyncio.run(
        event_bus.subscribe("DriverSearchRequested", assign_driver_use_case.execute)
    )
    asyncio.run(event_bus.subscribe("DriverAssigned", apply_driver_assigned_use_case.execute))
    asyncio.run(event_bus.subscribe("DriverAssigned", schedule_route_request))
    asyncio.run(event_bus.subscribe("RouteRequested", calculate_route_use_case.execute))
    asyncio.run(event_bus.subscribe("EtaUpdated", apply_eta_updated_use_case.execute))

    app.include_router(create_health_router(health_use_case))
    app.include_router(create_request_ride_router(request_ride_use_case))
    app.include_router(create_ride_status_router(ride_status_use_case))
    return app
