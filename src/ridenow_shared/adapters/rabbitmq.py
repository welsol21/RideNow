"""RabbitMQ-backed messaging adapters shared across RideNow services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust

from ridenow_shared.config.settings import RabbitMqSettings
from ridenow_shared.events import EventEnvelope
from ridenow_shared.retry import retry_async

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractChannel,
        AbstractConnection,
        AbstractExchange,
        AbstractIncomingMessage,
        AbstractQueue,
    )

    from ridenow_shared.contracts.messaging import EventHandler


class RabbitMqEventPublisher:
    """RabbitMQ event publisher backed by a durable topic exchange."""

    def __init__(
        self,
        connection: AbstractConnection,
        channel: AbstractChannel,
        exchange: AbstractExchange,
    ) -> None:
        """Store the transport objects used for publication."""

        self._connection = connection
        self._channel = channel
        self._exchange = exchange

    async def publish(self, event: EventEnvelope) -> None:
        """Publish an envelope using the payload name as the routing key."""

        await self._exchange.publish(
            Message(
                body=event.model_dump_json().encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=event.payload.name,
        )

    async def close(self) -> None:
        """Close the underlying channel and connection."""

        await self._channel.close()
        await self._connection.close()


class RabbitMqEventConsumer:
    """RabbitMQ event consumer backed by exclusive auto-delete queues."""

    def __init__(
        self,
        connection: AbstractConnection,
        channel: AbstractChannel,
        exchange: AbstractExchange,
    ) -> None:
        """Store the transport objects used for subscriptions."""

        self._connection = connection
        self._channel = channel
        self._exchange = exchange
        self._queues: list[AbstractQueue] = []

    async def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Subscribe an async handler to a RabbitMQ routing key."""

        queue = await self._channel.declare_queue(
            name="",
            exclusive=True,
            auto_delete=True,
        )
        await queue.bind(self._exchange, routing_key=topic)

        async def on_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=False):
                envelope = EventEnvelope.model_validate_json(message.body)
                await handler(envelope)

        await queue.consume(on_message)
        self._queues.append(queue)

    async def close(self) -> None:
        """Close any declared queues and then close the transport."""

        for queue in self._queues:
            await queue.delete(if_unused=False, if_empty=False)
        await self._channel.close()
        await self._connection.close()


async def create_event_publisher(
    settings: RabbitMqSettings | None = None,
) -> RabbitMqEventPublisher:
    """Create a connected RabbitMQ event publisher."""

    connection, channel, exchange = await _open_exchange(settings or RabbitMqSettings())
    return RabbitMqEventPublisher(
        connection=connection,
        channel=channel,
        exchange=exchange,
    )


async def create_event_consumer(
    settings: RabbitMqSettings | None = None,
) -> RabbitMqEventConsumer:
    """Create a connected RabbitMQ event consumer."""

    resolved_settings = settings or RabbitMqSettings()
    connection, channel, exchange = await _open_exchange(resolved_settings)
    await channel.set_qos(prefetch_count=resolved_settings.prefetch_count)
    return RabbitMqEventConsumer(
        connection=connection,
        channel=channel,
        exchange=exchange,
    )


async def _open_exchange(
    settings: RabbitMqSettings,
) -> tuple[
    AbstractConnection,
    AbstractChannel,
    AbstractExchange,
]:
    """Open the transport objects shared by publisher and consumer factories."""

    connection = await retry_async(lambda: connect_robust(settings.url))
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        settings.exchange,
        ExchangeType.TOPIC,
        durable=True,
    )
    return connection, channel, exchange
