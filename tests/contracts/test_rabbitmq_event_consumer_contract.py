"""Contract test for the RabbitMQ event consumer adapter."""

import pytest

from tests.contracts.contract_suites import assert_event_consumer_contract
from tests.support.rabbitmq import rabbitmq_publish_to_topic


@pytest.mark.contracts
@pytest.mark.integration
@pytest.mark.asyncio
async def test_rabbitmq_event_consumer_contract() -> None:
    """Verify the RabbitMQ consumer satisfies the shared consumer contract."""

    from ridenow_shared.adapters.rabbitmq import create_event_consumer

    async with rabbitmq_publish_to_topic() as publish_to_topic:
        await assert_event_consumer_contract(
            create_consumer=create_event_consumer,
            publish_to_topic=publish_to_topic,
        )
