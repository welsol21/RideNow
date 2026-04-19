"""Unit tests for Driver assignment behaviour."""

from ridenow_driver.core.application.assign_driver import AssignDriverUseCase
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_driver_service_publishes_driver_assigned_event() -> None:
    """Verify Driver publishes a deterministic driver assignment outcome."""

    publisher = RecordingEventPublisher()
    use_case = AssignDriverUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="DriverSearchRequested",
                data={"ride_id": "ride-1"},
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "driver"
    assert published.payload == DomainEventPayload(
        name="DriverAssigned",
        data={
            "ride_id": "ride-1",
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
    )


async def test_driver_service_can_publish_no_driver_available() -> None:
    """Verify Driver emits the no-driver outcome for unavailable supply."""

    publisher = RecordingEventPublisher()
    use_case = AssignDriverUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="DriverSearchRequested",
                data={
                    "ride_id": "ride-1",
                    "customer_id": "customer-no-driver",
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "driver"
    assert published.payload == DomainEventPayload(
        name="NoDriverAvailable",
        data={"ride_id": "ride-1"},
    )
