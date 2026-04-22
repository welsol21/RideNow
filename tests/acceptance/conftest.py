"""Shared fixtures for acceptance tests."""

from collections.abc import Iterator

import pytest
from tests.acceptance.support import BrokerAcceptanceClient


@pytest.fixture
def broker_client() -> Iterator[BrokerAcceptanceClient]:
    """Provide a Broker acceptance client for local or live mode."""

    client = BrokerAcceptanceClient()
    try:
        yield client
    finally:
        client.close()
