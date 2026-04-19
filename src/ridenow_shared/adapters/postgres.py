"""PostgreSQL-backed state-store adapters shared across RideNow services."""

from __future__ import annotations

from sqlalchemy import Column, MetaData, String, Table, select, text
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from ridenow_shared.config.settings import PostgresSettings


class PostgresStateStore:
    """PostgreSQL-backed JSON state store keyed by logical store and entity id."""

    def __init__(
        self,
        engine: AsyncEngine,
        state_table: Table,
        store_name: str,
    ) -> None:
        """Store the engine, shared table metadata, and logical store name."""

        self._engine = engine
        self._session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
        self._state_table = state_table
        self._store_name = store_name

    async def put(self, key: str, state: dict[str, object]) -> None:
        """Persist JSON state by logical store and entity key."""

        statement = insert(self._state_table).values(
            store_name=self._store_name,
            state_key=key,
            payload=state,
        )
        upsert = statement.on_conflict_do_update(
            index_elements=["store_name", "state_key"],
            set_={"payload": statement.excluded.payload},
        )
        async with self._session_factory() as session:
            await session.execute(upsert)
            await session.commit()

    async def get(self, key: str) -> dict[str, object] | None:
        """Load JSON state by logical store and entity key."""

        statement = (
            select(self._state_table.c.payload)
            .where(self._state_table.c.store_name == self._store_name)
            .where(self._state_table.c.state_key == key)
        )
        async with self._session_factory() as session:
            result = await session.execute(statement)
            payload = result.scalar_one_or_none()
        if payload is None:
            return None
        return dict(payload)

    async def close(self) -> None:
        """Dispose the underlying engine."""

        await self._engine.dispose()


async def create_state_store(
    *,
    store_name: str,
    table_name: str = "service_state",
    settings: PostgresSettings | None = None,
) -> PostgresStateStore:
    """Create a connected PostgreSQL-backed JSON state store."""

    resolved_settings = settings or PostgresSettings()
    engine = create_async_engine(resolved_settings.url)
    metadata = MetaData(schema=resolved_settings.schema_name)
    state_table = Table(
        table_name,
        metadata,
        Column("store_name", String(length=120), primary_key=True),
        Column("state_key", String(length=200), primary_key=True),
        Column("payload", JSONB, nullable=False),
    )

    async with engine.begin() as connection:
        if resolved_settings.schema_name != "public":
            await connection.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{resolved_settings.schema_name}"')
            )
        await connection.run_sync(metadata.create_all)

    return PostgresStateStore(
        engine=engine,
        state_table=state_table,
        store_name=store_name,
    )
