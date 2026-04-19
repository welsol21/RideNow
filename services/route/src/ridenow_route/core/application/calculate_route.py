"""Route use case that emits deterministic route and ETA feedback."""

from ridenow_route.core.application.ports import RouteEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class CalculateRouteUseCase:
    """Calculate customer-visible route and ETA information."""

    def __init__(self, event_publisher: RouteEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish deterministic route and ETA feedback for the requested ride."""

        ride_id = str(event.payload.data["ride_id"])
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="route",
                payload=DomainEventPayload(
                    name="EtaUpdated",
                    data={
                        "ride_id": ride_id,
                        "distance_km": 4.8,
                        "pickup_eta_minutes": 3,
                        "trip_duration_minutes": 11,
                    },
                ),
            )
        )
