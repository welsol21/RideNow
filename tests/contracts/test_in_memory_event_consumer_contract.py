"""Contract test for the in-memory event consumer adapter."""

import pytest

from ridenow_shared.adapters.in_memory.messaging import InMemoryEventBus
from tests.contracts.contract_suites import assert_event_consumer_contract


@pytest.mark.contracts
@pytest.mark.asyncio
async def test_in_memory_event_consumer_contract() -> None:
    """Verify the in-memory event consumer satisfies the shared contract."""

    bus = InMemoryEventBus()

    await assert_event_consumer_contract(
        create_consumer=lambda: bus,
        publish_to_topic=bus.publish_to_topic,
    )
