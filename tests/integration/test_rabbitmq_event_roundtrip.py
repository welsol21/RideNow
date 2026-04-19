"""Integration test proving the real RabbitMQ adapters can round-trip an event."""

import asyncio

import pytest

from ridenow_shared.events import DomainEventPayload, EventEnvelope


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rabbitmq_roundtrip_between_real_publisher_and_consumer() -> None:
    """Verify a published envelope is consumed through real RabbitMQ transport."""

    from ridenow_shared.adapters.rabbitmq import (
        create_event_consumer,
        create_event_publisher,
    )

    publisher = await create_event_publisher()
    consumer = await create_event_consumer()
    received: list[EventEnvelope] = []
    event = EventEnvelope(
        correlation_id="ride-roundtrip",
        source="notification",
        payload=DomainEventPayload(
            name="PaymentConfirmedVisible",
            data={"ride_id": "ride-roundtrip"},
        ),
    )
    event_seen = asyncio.Event()

    async def handler(envelope: EventEnvelope) -> None:
        received.append(envelope)
        event_seen.set()

    try:
        await consumer.subscribe("PaymentConfirmedVisible", handler)
        await publisher.publish(event)

        await asyncio.wait_for(event_seen.wait(), timeout=5)

        assert received == [event]
    finally:
        await consumer.close()
        await publisher.close()
