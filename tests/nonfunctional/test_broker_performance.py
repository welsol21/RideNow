"""Performance and lightweight load validation for the live Broker surface."""

from __future__ import annotations

from time import perf_counter

import pytest
from tests.nonfunctional.runtime_helpers import (
    broker_client,
    percentile_95,
    ride_request_payload,
)


@pytest.mark.nonfunctional
def test_broker_request_ride_acknowledgement_stays_within_load_budget() -> None:
    """Verify repeated ride submissions stay inside a pragmatic latency budget."""

    durations: list[float] = []

    with broker_client() as client:
        for sequence in range(1, 21):
            started_at = perf_counter()
            response = client.post("/rides", json=ride_request_payload(sequence))
            durations.append(perf_counter() - started_at)
            assert response.status_code == 202
            assert response.json()["status"] == "request-submitted"

    assert percentile_95(durations) < 0.25
    assert max(durations) < 0.5
