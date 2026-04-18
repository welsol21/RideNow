"""Contract test for the in-memory state-store adapter."""

import pytest

from ridenow_shared.adapters.in_memory.state_store import InMemoryStateStore
from tests.contracts.contract_suites import assert_state_store_contract


@pytest.mark.contracts
@pytest.mark.asyncio
async def test_in_memory_state_store_contract() -> None:
    """Verify the in-memory state store satisfies the shared contract."""

    await assert_state_store_contract(create_state_store=InMemoryStateStore)
