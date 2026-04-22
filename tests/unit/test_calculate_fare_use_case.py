"""Unit tests for Pricing fare calculation behaviour."""

from ridenow_pricing.core.application.calculate_fare import CalculateFareUseCase

from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_pricing_service_publishes_fare_estimate() -> None:
    """Verify Pricing publishes deterministic fare estimation."""

    publisher = RecordingEventPublisher()
    use_case = CalculateFareUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="FareRequested",
                data={
                    "ride_id": "ride-1",
                    "distance_km": 4.8,
                    "pickup_eta_minutes": 3,
                    "trip_duration_minutes": 11,
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "pricing"
    assert published.payload == DomainEventPayload(
        name="FareEstimated",
        data={
            "ride_id": "ride-1",
            "amount": 18.5,
            "currency": "EUR",
        },
    )
