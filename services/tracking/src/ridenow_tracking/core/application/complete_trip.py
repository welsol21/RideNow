"""Tracking use case that emits deterministic trip completion."""

from ridenow_shared.events import DomainEventPayload, EventEnvelope
from ridenow_tracking.core.application.ports import TrackingEventPublisher


class CompleteTripUseCase:
    """Emit trip completion from tracking input events."""

    def __init__(self, event_publisher: TrackingEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish deterministic trip completion for the requested ride."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="tracking",
                payload=DomainEventPayload(
                    name="TripCompleted",
                    data={
                        "ride_id": str(event.payload.data["ride_id"]),
                        "driver_lat": float(event.payload.data["driver_lat"]),
                        "driver_lon": float(event.payload.data["driver_lon"]),
                    },
                ),
            )
        )
