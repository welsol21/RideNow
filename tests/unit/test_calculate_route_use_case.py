"""Unit tests for Route ETA calculation behaviour."""

from ridenow_route.core.application.calculate_route import CalculateRouteUseCase
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_route_service_publishes_eta_updated_event() -> None:
    """Verify Route publishes deterministic route and ETA feedback."""

    publisher = RecordingEventPublisher()
    use_case = CalculateRouteUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="RouteRequested",
                data={
                    "ride_id": "ride-1",
                    "driver_id": "driver-1",
                    "vehicle_id": "vehicle-1",
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "route"
    assert published.payload == DomainEventPayload(
        name="EtaUpdated",
        data={
            "ride_id": "ride-1",
            "distance_km": 4.8,
            "pickup_eta_minutes": 3,
            "trip_duration_minutes": 11,
        },
    )
