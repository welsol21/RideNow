"""PostgreSQL test helpers for real state-store contract and integration tests."""

from uuid import uuid4

from ridenow_shared.config.settings import PostgresSettings


def unique_store_name(prefix: str = "test-store") -> str:
    """Return a unique logical store name for an isolated test run."""

    return f"{prefix}-{uuid4().hex}"


def postgres_test_settings() -> PostgresSettings:
    """Return host-side PostgreSQL settings for integration tests."""

    return PostgresSettings(
        url="postgresql+asyncpg://postgres:postgres@127.0.0.1:15432/ridenow"
    )
