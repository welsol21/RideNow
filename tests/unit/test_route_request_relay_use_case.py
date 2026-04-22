"""Unit tests for Notification relay of route requests."""

from ridenow_notification.core.application.relay_route_request import (
    RelayRouteRequestUseCase,
)

from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_notification_relays_driver_assignment_to_route_request() -> None:
    """Verify Notification turns DriverAssigned into RouteRequested."""

    publisher = RecordingEventPublisher()
    use_case = RelayRouteRequestUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="driver",
            payload=DomainEventPayload(
                name="DriverAssigned",
                data={
                    "ride_id": "ride-1",
                    "driver_id": "driver-1",
                    "vehicle_id": "vehicle-1",
                    "pickup": {"lat": 53.3498, "lon": -6.2603},
                    "dropoff": {"lat": 53.3440, "lon": -6.2672},
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="RouteRequested",
        data={
            "ride_id": "ride-1",
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )
