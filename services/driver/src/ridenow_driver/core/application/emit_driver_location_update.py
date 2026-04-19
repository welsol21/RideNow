"""Driver use case that emits deterministic live progress updates."""

from ridenow_driver.core.application.ports import DriverEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class EmitDriverLocationUpdateUseCase:
    """Start trip-progress updates after payment authorisation."""

    def __init__(self, event_publisher: DriverEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a deterministic driver location update for the ride."""

        ride_id = str(event.payload.data["ride_id"])
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="driver",
                payload=DomainEventPayload(
                    name="DriverLocationUpdated",
                    data={
                        "ride_id": ride_id,
                        "driver_lat": 53.3472,
                        "driver_lon": -6.2591,
                    },
                ),
            )
        )
