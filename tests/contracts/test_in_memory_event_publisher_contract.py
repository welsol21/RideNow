"""Contract test for the in-memory event publisher adapter."""

import pytest

from ridenow_shared.adapters.in_memory.messaging import InMemoryEventPublisher
from tests.contracts.contract_suites import assert_event_publisher_contract


@pytest.mark.contracts
@pytest.mark.asyncio
async def test_in_memory_event_publisher_contract() -> None:
    """Verify the in-memory event publisher satisfies the shared contract."""

    published_events: list[object] = []

    await assert_event_publisher_contract(
        create_publisher=lambda: InMemoryEventPublisher(published_events),
        published_events=lambda: published_events,
    )
