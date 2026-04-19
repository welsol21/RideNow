"""Broker use case that acknowledges customer issue submissions."""

from dataclasses import dataclass

from ridenow_broker.core.application.ports import BrokerEventPublisher, IssueStore
from ridenow_shared.events import DomainEventPayload, EventEnvelope


@dataclass(frozen=True)
class IssueSubmissionCommand:
    """Command payload for a customer issue submission."""

    ride_id: str
    customer_id: str
    category: str
    description: str


@dataclass(frozen=True)
class IssueSubmissionResult:
    """Customer-visible acknowledgement returned by issue submission."""

    issue_id: str
    status: str


class IssueSubmissionUseCase:
    """Use case that acknowledges and publishes customer issue submissions."""

    def __init__(
        self,
        issue_store: IssueStore,
        event_publisher: BrokerEventPublisher,
    ) -> None:
        """Store outbound dependencies used by the use case."""

        self._issue_store = issue_store
        self._event_publisher = event_publisher

    async def execute(self, command: IssueSubmissionCommand) -> IssueSubmissionResult:
        """Persist the issue and publish an IssueSubmitted event."""

        issue_id = "issue-1"
        await self._issue_store.put(
            issue_id,
            {
                "ride_id": command.ride_id,
                "customer_id": command.customer_id,
                "category": command.category,
                "description": command.description,
                "status": "issue-submitted",
            },
        )
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=issue_id,
                source="broker",
                payload=DomainEventPayload(
                    name="IssueSubmitted",
                    data={
                        "issue_id": issue_id,
                        "ride_id": command.ride_id,
                        "customer_id": command.customer_id,
                        "category": command.category,
                        "description": command.description,
                    },
                ),
            )
        )
        return IssueSubmissionResult(issue_id=issue_id, status="issue-submitted")
