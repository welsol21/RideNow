"""Support helpers for local and live Broker acceptance tests."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass

from fastapi.testclient import TestClient
from ridenow_broker.bootstrap.app import create_app


@dataclass(frozen=True)
class AcceptanceResponse:
    """Small response wrapper shared by local and live acceptance modes."""

    status_code: int
    payload: object

    def json(self) -> object:
        """Return the decoded payload."""

        return self.payload


class BrokerAcceptanceClient:
    """Acceptance client that can target local TestClient or live HTTP."""

    def __init__(self) -> None:
        """Initialise the client in local or live mode."""

        self._mode = os.getenv("RIDENOW_ACCEPTANCE_MODE", "local")
        self._base_url = os.getenv("RIDENOW_BROKER_BASE_URL", "http://127.0.0.1:8001")
        self._client = TestClient(create_app()) if self._mode == "local" else None

    def close(self) -> None:
        """Close the local client when present."""

        if self._client is not None:
            self._client.close()

    def get(self, path: str) -> AcceptanceResponse:
        """Execute a GET request against the configured Broker target."""

        if self._client is not None:
            response = self._client.get(path)
            return AcceptanceResponse(response.status_code, response.json())
        with urllib.request.urlopen(f"{self._base_url}{path}", timeout=5) as response:
            return AcceptanceResponse(
                response.status,
                json.loads(response.read().decode()),
            )

    def post(self, path: str, payload: dict[str, object]) -> AcceptanceResponse:
        """Execute a POST request against the configured Broker target."""

        if self._client is not None:
            response = self._client.post(path, json=payload)
            return AcceptanceResponse(response.status_code, response.json())

        request = urllib.request.Request(
            f"{self._base_url}{path}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return AcceptanceResponse(
                response.status,
                json.loads(response.read().decode()),
            )

    def wait_for_status(
        self,
        ride_id: str,
        expected_status: str,
        *,
        attempts: int = 40,
        sleep_seconds: float = 0.1,
    ) -> AcceptanceResponse:
        """Poll ride status until the expected customer-visible state appears."""

        response = self.get(f"/rides/{ride_id}")
        for _ in range(attempts):
            payload = response.json()
            if isinstance(payload, dict) and payload.get("status") == expected_status:
                return response
            time.sleep(sleep_seconds)
            response = self.get(f"/rides/{ride_id}")
        return response
