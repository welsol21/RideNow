"""Acceptance test for issue submission acknowledgement."""

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.mark.acceptance
def test_issue_submission_returns_traceable_acknowledgement(
    broker_client: BrokerAcceptanceClient,
) -> None:
    """Verify that an issue submission is acknowledged immediately."""

    response = broker_client.post(
        "/issues",
        {
            "ride_id": "ride-1",
            "customer_id": "customer-1",
            "category": "payment",
            "description": "Payment captured twice.",
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "issue-submitted"
    assert str(payload["issue_id"]).startswith("issue-")
