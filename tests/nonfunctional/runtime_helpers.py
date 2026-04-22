"""Helpers for Compose-backed nonfunctional RideNow tests."""

from __future__ import annotations

import math
import os
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path

import httpx

BROKER_BASE_URL = "http://127.0.0.1:8001"
PROMETHEUS_BASE_URL = "http://127.0.0.1:9090"
REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = (
    REPO_ROOT / "infra" / "compose" / "docker-compose.yml"
)


def broker_client() -> httpx.Client:
    """Create a short-lived client for the public Broker surface."""

    return httpx.Client(base_url=BROKER_BASE_URL, timeout=5.0)


def prometheus_client() -> httpx.Client:
    """Create a short-lived client for the Prometheus HTTP API."""

    return httpx.Client(base_url=PROMETHEUS_BASE_URL, timeout=5.0)


def ride_request_payload(sequence: int) -> dict[str, object]:
    """Build a unique ride request payload for load and soak scenarios."""

    return {
        "customer_id": f"customer-nf-{sequence}",
        "pickup": {"lat": 53.3498 + sequence * 0.0001, "lon": -6.2603},
        "dropoff": {"lat": 53.3440, "lon": -6.2672 - sequence * 0.0001},
    }


def percentile_95(samples: list[float]) -> float:
    """Return the nearest-rank p95 for a non-empty sample set."""

    ordered = sorted(samples)
    index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return ordered[index]


def wait_for_broker_readiness(timeout_seconds: float = 30.0) -> None:
    """Poll the Broker `/ready` endpoint until it returns healthy readiness."""

    deadline = time.monotonic() + timeout_seconds
    with broker_client() as client:
        while time.monotonic() < deadline:
            try:
                response = client.get("/ready")
            except httpx.HTTPError:
                time.sleep(0.5)
                continue
            if response.status_code == 200 and response.json()["status"] == "ready":
                return
            time.sleep(0.5)
    raise AssertionError("broker did not become ready within the nonfunctional timeout")


def restart_compose_service(service_name: str) -> None:
    """Restart a Compose service from the host environment."""

    docker_config = REPO_ROOT / ".tmp-docker-config"
    docker_config.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["DOCKER_CONFIG"] = str(docker_config)
    subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(COMPOSE_FILE),
            "restart",
            service_name,
        ],
        check=True,
        capture_output=True,
        env=environment,
        text=True,
    )


def prometheus_query(query: str) -> dict[str, object]:
    """Execute a Prometheus instant query and return the JSON payload."""

    with prometheus_client() as client:
        response = client.get("/api/v1/query", params={"query": query})
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise AssertionError("unexpected Prometheus response payload")
    return dict(payload)
