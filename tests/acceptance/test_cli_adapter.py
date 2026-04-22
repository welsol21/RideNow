"""Acceptance tests for the Broker CLI inbound adapter."""

import json

import pytest
from ridenow_broker.adapters.cli import main


@pytest.mark.acceptance
def test_cli_health_command_returns_service_status(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify the CLI can expose the Broker health check."""

    exit_code = main(["health"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "service": "broker",
        "status": "ok",
    }


@pytest.mark.acceptance
def test_cli_request_ride_command_returns_acknowledgement(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify the CLI can submit a ride request and print the acknowledgement."""

    exit_code = main(
        [
            "request-ride",
            "--customer-id",
            "customer-1",
            "--pickup-lat",
            "53.3498",
            "--pickup-lon",
            "-6.2603",
            "--dropoff-lat",
            "53.3440",
            "--dropoff-lon",
            "-6.2672",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "ride_id": "ride-1",
        "status": "request-submitted",
    }


@pytest.mark.acceptance
def test_cli_submit_issue_command_returns_traceable_acknowledgement(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify the CLI can submit an issue and print the acknowledgement."""

    exit_code = main(
        [
            "submit-issue",
            "--ride-id",
            "ride-1",
            "--customer-id",
            "customer-1",
            "--category",
            "payment",
            "--description",
            "Payment captured twice.",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "issue_id": "issue-1",
        "status": "issue-submitted",
    }
