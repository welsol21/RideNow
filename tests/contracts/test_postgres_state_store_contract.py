"""Contract test for the PostgreSQL state-store adapter."""

import pytest

from tests.contracts.contract_suites import assert_state_store_contract
from tests.support.postgres import postgres_test_settings, unique_store_name


@pytest.mark.contracts
@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_state_store_contract() -> None:
    """Verify the PostgreSQL store satisfies the shared state-store contract."""

    from ridenow_shared.adapters.postgres import create_state_store

    store_name = unique_store_name("contract")

    await assert_state_store_contract(
        create_state_store=lambda: create_state_store(
            store_name=store_name,
            settings=postgres_test_settings(),
        )
    )
