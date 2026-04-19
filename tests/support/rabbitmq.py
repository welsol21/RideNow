"""RabbitMQ test helpers for real adapter contract and integration tests."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from uuid import uuid4

from aio_pika import ExchangeType, connect_robust

from ridenow_shared.config.settings import RabbitMqSettings
from ridenow_shared.events import EventEnvelope

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable

    from aio_pika.abc import (
        AbstractChannel,
        AbstractConnection,
        AbstractExchange,
        AbstractQueue,
    )


async def _open_exchange() -> tuple[
    AbstractConnection,
    AbstractChannel,
    AbstractExchange,
]:
    """Open a robust connection/channel/exchange triple for tests."""

    settings = RabbitMqSettings()
    connection = await connect_robust(settings.url)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        settings.exchange,
        ExchangeType.TOPIC,
        durable=True,
    )
    return connection, channel, exchange


@asynccontextmanager
async def capture_topic(
    topic: str,
) -> AsyncIterator[Callable[[], Awaitable[list[EventEnvelope]]]]:
    """Capture all envelopes published to a topic during the context."""

    connection, channel, exchange = await _open_exchange()
    queue = await channel.declare_queue(
        name=f"test.capture.{topic}.{uuid4()}",
        exclusive=True,
        auto_delete=True,
    )
    await queue.bind(exchange, routing_key=topic)

    async def read_once() -> list[EventEnvelope]:
        message = await queue.get(timeout=5, fail=True)
        await message.ack()
        return [EventEnvelope.model_validate_json(message.body)]

    try:
        yield read_once
    finally:
        await _close_queue(queue)
        await channel.close()
        await connection.close()


@asynccontextmanager
async def rabbitmq_publish_to_topic() -> AsyncIterator[
    Callable[[str, EventEnvelope], Awaitable[None]]
]:
    """Provide a helper that publishes raw envelopes to a topic."""

    from aio_pika import DeliveryMode, Message

    connection, channel, exchange = await _open_exchange()

    async def publish_to_topic(topic: str, event: EventEnvelope) -> None:
        await exchange.publish(
            Message(
                body=event.model_dump_json().encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=topic,
        )

    try:
        yield publish_to_topic
    finally:
        await channel.close()
        await connection.close()


async def _close_queue(queue: AbstractQueue) -> None:
    """Close a test queue without leaking a failure into the test outcome."""

    await queue.delete(if_unused=False, if_empty=False)
