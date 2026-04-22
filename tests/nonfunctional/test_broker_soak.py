"""Short soak-style reliability scaffold for the live RideNow stack."""

from __future__ import annotations

import time

import pytest
from tests.nonfunctional.runtime_helpers import broker_client, ride_request_payload


@pytest.mark.nonfunctional
def test_broker_short_soak_scaffold_runs_without_submission_failures() -> None:
    """Verify a short sustained submission loop completes without request failures."""

    accepted = 0
    started_at = time.monotonic()

    with broker_client() as client:
        for sequence in range(300, 310):
            response = client.post("/rides", json=ride_request_payload(sequence))
            assert response.status_code == 202
            accepted += 1
            time.sleep(0.1)

    assert accepted == 10
    assert time.monotonic() - started_at < 8.0
