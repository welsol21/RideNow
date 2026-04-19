"""Contract test for the RabbitMQ event publisher adapter."""

import pytest

from tests.contracts.contract_suites import assert_event_publisher_contract
from tests.support.rabbitmq import capture_topic


@pytest.mark.contracts
@pytest.mark.integration
@pytest.mark.asyncio
async def test_rabbitmq_event_publisher_contract() -> None:
    """Verify the RabbitMQ publisher satisfies the shared publisher contract."""

    from ridenow_shared.adapters.rabbitmq import create_event_publisher

    async with capture_topic("RideRequested") as published_events:
        await assert_event_publisher_contract(
            create_publisher=create_event_publisher,
            published_events=published_events,
        )
