"""Integration matrix for full-system startup and readiness."""

from importlib import import_module

import pytest
from fastapi.testclient import TestClient


SERVICE_MODULES = {
    "broker": "ridenow_broker.bootstrap.app",
    "driver": "ridenow_driver.bootstrap.app",
    "route": "ridenow_route.bootstrap.app",
    "pricing": "ridenow_pricing.bootstrap.app",
    "payment": "ridenow_payment.bootstrap.app",
    "tracking": "ridenow_tracking.bootstrap.app",
    "notification": "ridenow_notification.bootstrap.app",
}


@pytest.mark.integration
@pytest.mark.parametrize(("service_name", "module_name"), SERVICE_MODULES.items())
def test_each_service_starts_and_reports_health_and_readiness(
    service_name: str, module_name: str
) -> None:
    """Verify that each service can start and expose health/readiness probes."""

    module = import_module(module_name)
    app = module.create_app()
    client = TestClient(app)

    health_response = client.get("/health")
    readiness_response = client.get("/ready")

    assert health_response.status_code == 200
    assert health_response.json() == {
        "service": service_name,
        "status": "ok",
    }
    assert readiness_response.status_code == 200
    assert readiness_response.json() == {
        "service": service_name,
        "status": "ready",
    }
