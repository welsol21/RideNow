"""Shared event models for inter-service communication."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DomainEventPayload(BaseModel):
    """Generic event payload.

    Parameters:
        name: Domain event name.
        data: Event payload body.
    Return value:
        Structured domain event payload.
    Exceptions raised:
        ValidationError: If values do not satisfy declared types.
    Example:
        DomainEventPayload(name="RideRequested", data={"ride_id": "r-1"})
    """

    name: str = Field(min_length=1)
    data: dict[str, Any] = Field(default_factory=dict)


class EventEnvelope(BaseModel):
    """Transport envelope for shared events.

    Parameters:
        event_id: Globally unique event identifier.
        correlation_id: Workflow correlation identifier.
        source: Service that emitted the event.
        occurred_at: UTC timestamp for event emission.
        payload: Domain payload carried by the event.
    Return value:
        Immutable event envelope for the message backbone.
    Exceptions raised:
        ValidationError: If values do not satisfy declared types.
    Example:
        EventEnvelope(
            correlation_id="ride-123",
            source="broker",
            payload=DomainEventPayload(name="RideRequested"),
        )
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: DomainEventPayload
