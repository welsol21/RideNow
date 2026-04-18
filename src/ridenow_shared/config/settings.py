"""Shared runtime settings for RideNow services."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMqSettings(BaseSettings):
    """RabbitMQ connection settings.

    Parameters:
        url: AMQP connection string for the service.
        exchange: Exchange used for cross-service events.
        prefetch_count: Consumer prefetch window.
    Return value:
        Instance holding RabbitMQ runtime configuration.
    Exceptions raised:
        ValidationError: If values do not satisfy declared types.
    Example:
        RabbitMqSettings(url="amqp://guest:guest@localhost:5672/")
    """

    model_config = SettingsConfigDict(env_prefix="RIDENOW_RABBITMQ_", extra="ignore")

    url: str = Field(default="amqp://guest:guest@localhost:5672/")
    exchange: str = Field(default="ridenow.events")
    prefetch_count: int = Field(default=10, ge=1)


class PostgresSettings(BaseSettings):
    """PostgreSQL connection settings.

    Parameters:
        url: SQLAlchemy-compatible database URL.
        schema: Logical schema name for service tables.
    Return value:
        Instance holding PostgreSQL runtime configuration.
    Exceptions raised:
        ValidationError: If values do not satisfy declared types.
    Example:
        PostgresSettings(url="postgresql+asyncpg://postgres:postgres@localhost:5432/ridenow")
    """

    model_config = SettingsConfigDict(env_prefix="RIDENOW_POSTGRES_", extra="ignore")

    url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ridenow"
    )
    schema: str = Field(default="public")


class HttpSettings(BaseSettings):
    """HTTP adapter settings shared by services.

    Parameters:
        host: Bind host.
        port: Bind port.
        log_level: HTTP server log level.
    Return value:
        Instance holding HTTP runtime configuration.
    Exceptions raised:
        ValidationError: If values do not satisfy declared types.
    Example:
        HttpSettings(port=8000)
    """

    model_config = SettingsConfigDict(env_prefix="RIDENOW_HTTP_", extra="ignore")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = Field(default="info")


class SharedServiceSettings(BaseSettings):
    """Top-level shared service settings.

    Parameters:
        service_name: Logical service name used in logs and events.
        environment: Runtime environment label.
        http: HTTP settings object.
        rabbitmq: RabbitMQ settings object.
        postgres: PostgreSQL settings object.
    Return value:
        Aggregate shared settings instance.
    Exceptions raised:
        ValidationError: If nested settings are invalid.
    Example:
        SharedServiceSettings(service_name="broker")
    """

    model_config = SettingsConfigDict(env_prefix="RIDENOW_", extra="ignore")

    service_name: str
    environment: str = Field(default="local")
    http: HttpSettings = Field(default_factory=HttpSettings)
    rabbitmq: RabbitMqSettings = Field(default_factory=RabbitMqSettings)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
