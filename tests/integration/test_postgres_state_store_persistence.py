"""Integration test proving PostgreSQL-backed state persists across instances."""

import pytest
from tests.support.postgres import postgres_test_settings, unique_store_name

from ridenow_shared.adapters.postgres import create_state_store


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_state_store_persists_state_across_instances() -> None:
    """Verify persisted state survives across independent store instances."""

    store_name = unique_store_name("persistence")
    ride_id = "ride-postgres-1"
    state: dict[str, object] = {
        "status": "payment-confirmed",
        "driver": {"driver_id": "driver-7"},
    }
    settings = postgres_test_settings()

    writer = await create_state_store(store_name=store_name, settings=settings)
    await writer.put(ride_id, state)
    await writer.close()

    reader = await create_state_store(store_name=store_name, settings=settings)
    try:
        assert await reader.get(ride_id) == state
    finally:
        await reader.close()
