"""Acceptance test for issue submission acknowledgement."""

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_issue_submission_returns_traceable_acknowledgement() -> None:
    """Verify that an issue submission is acknowledged immediately."""

    client = TestClient(create_app())

    response = client.post(
        "/issues",
        json={
            "ride_id": "ride-1",
            "customer_id": "customer-1",
            "category": "payment",
            "description": "Payment captured twice.",
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "issue_id": "issue-1",
        "status": "issue-submitted",
    }
