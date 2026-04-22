"""Unit tests for Broker issue submission use case."""

from ridenow_broker.core.application.issue_submission import (
    IssueSubmissionCommand,
    IssueSubmissionResult,
    IssueSubmissionUseCase,
)

from ridenow_shared.events import EventEnvelope


class RecordingIssueStore:
    """Test double capturing persisted issue records."""

    def __init__(self) -> None:
        """Initialise the in-memory issue dictionary."""

        self.saved: dict[str, dict[str, object]] = {}

    async def put(self, key: str, state: dict[str, object]) -> None:
        """Persist issue state by key."""

        self.saved[key] = state

    async def get(self, key: str) -> dict[str, object] | None:
        """Return issue state by key if present."""

        return self.saved.get(key)


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_issue_submission_acknowledges_and_publishes() -> None:
    """Verify the use case persists issue state and publishes IssueSubmitted."""

    store = RecordingIssueStore()
    publisher = RecordingEventPublisher()
    use_case = IssueSubmissionUseCase(issue_store=store, event_publisher=publisher)

    result = await use_case.execute(
        IssueSubmissionCommand(
            ride_id="ride-1",
            customer_id="customer-1",
            category="payment",
            description="Payment captured twice.",
        )
    )

    assert result == IssueSubmissionResult(
        issue_id="issue-1",
        status="issue-submitted",
    )
    assert store.saved == {
        "issue-1": {
            "ride_id": "ride-1",
            "customer_id": "customer-1",
            "category": "payment",
            "description": "Payment captured twice.",
            "status": "issue-submitted",
        }
    }
    assert len(publisher.events) == 1
    assert publisher.events[0].payload.name == "IssueSubmitted"
    assert publisher.events[0].payload.data == {
        "issue_id": "issue-1",
        "ride_id": "ride-1",
        "customer_id": "customer-1",
        "category": "payment",
        "description": "Payment captured twice.",
    }
