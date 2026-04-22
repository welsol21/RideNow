"""Integration coverage for structured HTTP request logging."""

from __future__ import annotations

import io
import json

from fastapi.testclient import TestClient

from ridenow_shared import configure_structured_logging, create_probe_app


def test_probe_app_emits_json_request_logs() -> None:
    """Verify probe apps emit structured JSON logs for HTTP requests."""

    stream = io.StringIO()
    configure_structured_logging(stream=stream, force=True)
    client = TestClient(create_probe_app("driver"))

    response = client.get("/health")

    configure_structured_logging(force=True)

    assert response.status_code == 200
    entries = [
        json.loads(line)
        for line in stream.getvalue().splitlines()
        if line.strip().startswith("{")
    ]
    assert entries[-1]["event"] == "http_request"
    assert entries[-1]["service"] == "driver"
    assert entries[-1]["method"] == "GET"
    assert entries[-1]["path"] == "/health"
    assert entries[-1]["status_code"] == 200
