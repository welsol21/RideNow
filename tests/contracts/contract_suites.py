"""Shared contract suites for outbound RideNow ports."""

from collections.abc import Awaitable, Callable

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore
from ridenow_shared.events import DomainEventPayload, EventEnvelope


async def assert_event_publisher_contract(
    create_publisher: Callable[[], EventPublisher],
    published_events: Callable[[], list[EventEnvelope]],
) -> None:
    """Assert the contract for an event publisher implementation."""

    publisher = create_publisher()
    event = EventEnvelope(
        correlation_id="ride-1",
        source="broker",
        payload=DomainEventPayload(name="RideRequested", data={"ride_id": "ride-1"}),
    )

    await publisher.publish(event)

    assert published_events() == [event]


async def assert_event_consumer_contract(
    create_consumer: Callable[[], EventConsumer],
    publish_to_topic: Callable[[str, EventEnvelope], Awaitable[None]],
) -> None:
    """Assert the contract for an event consumer implementation."""

    consumer = create_consumer()
    received: list[EventEnvelope] = []
    event = EventEnvelope(
        correlation_id="ride-2",
        source="driver",
        payload=DomainEventPayload(name="DriverAssigned", data={"ride_id": "ride-2"}),
    )

    async def handler(envelope: EventEnvelope) -> None:
        received.append(envelope)

    await consumer.subscribe("ride.assigned", handler)
    await publish_to_topic("ride.assigned", event)

    assert received == [event]


async def assert_state_store_contract(
    create_state_store: Callable[[], StateStore[dict[str, object]]],
) -> None:
    """Assert the contract for a state-store implementation."""

    store = create_state_store()
    key = "ride-3"
    state = {"status": "driver-assigned", "driver_id": "driver-7"}

    assert await store.get(key) is None

    await store.put(key, state)

    assert await store.get(key) == state
