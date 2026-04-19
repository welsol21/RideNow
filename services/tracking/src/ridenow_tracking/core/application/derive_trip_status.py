"""Tracking use case that emits deterministic trip-progress feedback."""

from ridenow_shared.events import DomainEventPayload, EventEnvelope
from ridenow_tracking.core.application.ports import TrackingEventPublisher


class DeriveTripStatusUseCase:
    """Derive customer-visible trip status from location updates."""

    def __init__(self, event_publisher: TrackingEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish deterministic trip-progress feedback for the requested ride."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="tracking",
                payload=DomainEventPayload(
                    name="TripStatusUpdated",
                    data={
                        "ride_id": str(event.payload.data["ride_id"]),
                        "phase": "driver-arriving",
                        "driver_lat": float(event.payload.data["driver_lat"]),
                        "driver_lon": float(event.payload.data["driver_lon"]),
                    },
                ),
            )
        )
