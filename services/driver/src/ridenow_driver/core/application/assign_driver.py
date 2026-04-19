"""Driver use case that emits a deterministic driver assignment outcome."""

from ridenow_driver.core.application.ports import DriverEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class AssignDriverUseCase:
    """Assign a driver for an inbound driver-search request."""

    def __init__(self, event_publisher: DriverEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish the driver assignment outcome for the requested ride."""

        ride_id = str(event.payload.data["ride_id"])
        if event.payload.data.get("customer_id") == "customer-no-driver":
            await self._event_publisher.publish(
                EventEnvelope(
                    correlation_id=event.correlation_id,
                    source="driver",
                    payload=DomainEventPayload(
                        name="NoDriverAvailable",
                        data={"ride_id": ride_id},
                    ),
                )
            )
            return
        assignment_data: dict[str, object] = {
            "ride_id": ride_id,
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        }
        if "pickup" in event.payload.data:
            assignment_data["pickup"] = event.payload.data["pickup"]
        if "dropoff" in event.payload.data:
            assignment_data["dropoff"] = event.payload.data["dropoff"]
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="driver",
                payload=DomainEventPayload(
                    name="DriverAssigned",
                    data=assignment_data,
                ),
            )
        )
