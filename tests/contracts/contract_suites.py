"""Shared contract suites for outbound RideNow ports."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore
from ridenow_shared.events import DomainEventPayload, EventEnvelope

T = TypeVar("T")


async def _resolve(value: T | Awaitable[T]) -> T:
    """Resolve either an eager value or an awaitable value."""

    if isinstance(value, Awaitable):
        return await value
    return value


async def _maybe_close(resource: object) -> None:
    """Close a test resource if it exposes an async close method."""

    close = getattr(resource, "close", None)
    if close is None:
        return
    result = close()
    if isinstance(result, Awaitable):
        await result


async def assert_event_publisher_contract(
    create_publisher: Callable[[], EventPublisher | Awaitable[EventPublisher]],
    published_events: Callable[
        [], list[EventEnvelope] | Awaitable[list[EventEnvelope]]
    ],
) -> None:
    """Assert the contract for an event publisher implementation."""

    publisher = await _resolve(create_publisher())
    event = EventEnvelope(
        correlation_id="ride-1",
        source="broker",
        payload=DomainEventPayload(name="RideRequested", data={"ride_id": "ride-1"}),
    )

    try:
        await publisher.publish(event)

        assert await _resolve(published_events()) == [event]
    finally:
        await _maybe_close(publisher)


async def assert_event_consumer_contract(
    create_consumer: Callable[[], EventConsumer | Awaitable[EventConsumer]],
    publish_to_topic: Callable[[str, EventEnvelope], Awaitable[None]],
) -> None:
    """Assert the contract for an event consumer implementation."""

    consumer = await _resolve(create_consumer())
    received: list[EventEnvelope] = []
    received_event = asyncio.Event()
    event = EventEnvelope(
        correlation_id="ride-2",
        source="driver",
        payload=DomainEventPayload(name="DriverAssigned", data={"ride_id": "ride-2"}),
    )

    async def handler(envelope: EventEnvelope) -> None:
        received.append(envelope)
        received_event.set()

    try:
        await consumer.subscribe("ride.assigned", handler)
        await publish_to_topic("ride.assigned", event)
        await asyncio.wait_for(received_event.wait(), timeout=5)

        assert received == [event]
    finally:
        await _maybe_close(consumer)


async def assert_state_store_contract(
    create_state_store: Callable[
        [], StateStore[dict[str, object]] | Awaitable[StateStore[dict[str, object]]]
    ],
) -> None:
    """Assert the contract for a state-store implementation."""

    store = await _resolve(create_state_store())
    key = "ride-3"
    state: dict[str, object] = {
        "status": "driver-assigned",
        "driver_id": "driver-7",
    }

    assert await store.get(key) is None

    await store.put(key, state)

    assert await store.get(key) == state
