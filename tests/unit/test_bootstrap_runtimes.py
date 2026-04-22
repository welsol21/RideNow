"""Unit coverage for real runtime bootstrap wiring and shared startup helpers."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import pytest
from fastapi.testclient import TestClient
from ridenow_broker.core.application import IssueSubmissionCommand, RequestRideCommand

from ridenow_shared.bootstrap import delayed_event_handler, run_service_app
from ridenow_shared.config import SharedServiceSettings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class FakePublisher:
    """Async publisher test double tracking close calls and published events."""

    def __init__(self) -> None:
        self.closed = False
        self.published: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.published.append(event)

    async def close(self) -> None:
        self.closed = True


class FakeConsumer:
    """Async consumer test double tracking subscriptions and close calls."""

    def __init__(self) -> None:
        self.closed = False
        self.subscriptions: list[str] = []

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Any], Awaitable[None]],
    ) -> None:
        self.subscriptions.append(topic)

    async def close(self) -> None:
        self.closed = True


class FakeStateStore:
    """Async state-store test double for broker runtime wiring."""

    def __init__(self) -> None:
        self.closed = False
        self.values: dict[str, dict[str, object]] = {}

    async def put(self, key: str, value: dict[str, object]) -> None:
        self.values[key] = value

    async def get(self, key: str) -> dict[str, object] | None:
        return self.values.get(key)

    async def close(self) -> None:
        self.closed = True


class DummyAsyncUseCase:
    """Trivial async use case placeholder for unused broker routes."""

    async def execute(self, *args: object, **kwargs: object) -> object:
        return {"unused": True}


class DummyHealthUseCase:
    """Trivial sync health use case for broker app startup tests."""

    def execute(self) -> object:
        return SimpleNamespace(service="broker", status="ok")


class FakeBrokerAppRuntime:
    """Minimal runtime required to build the broker HTTP app."""

    def __init__(self) -> None:
        self.closed = False
        self.health_check = DummyHealthUseCase()
        self.request_ride = DummyAsyncUseCase()
        self.issue_submission = DummyAsyncUseCase()
        self.ride_status = DummyAsyncUseCase()

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_broker_real_runtime_uses_unique_identifiers_and_subscriptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify Broker real runtime wires subscriptions and avoids reused ids."""

    module = importlib.import_module("ridenow_broker.bootstrap.real_runtime")
    publisher = FakePublisher()
    consumer = FakeConsumer()
    ride_store = FakeStateStore()
    issue_store = FakeStateStore()

    async def fake_create_event_publisher(settings: object) -> FakePublisher:
        return publisher

    async def fake_create_event_consumer(settings: object) -> FakeConsumer:
        return consumer

    async def fake_create_state_store(
        *,
        store_name: str,
        settings: object,
    ) -> FakeStateStore:
        return ride_store if store_name == "broker-ride-status" else issue_store

    monkeypatch.setattr(module, "create_event_publisher", fake_create_event_publisher)
    monkeypatch.setattr(module, "create_event_consumer", fake_create_event_consumer)
    monkeypatch.setattr(module, "create_state_store", fake_create_state_store)

    runtime = await module.create_real_runtime(
        SharedServiceSettings(service_name="broker")
    )

    first_ride = await runtime.request_ride.execute(
        RequestRideCommand(
            customer_id="customer-1",
            pickup={"lat": 53.0, "lon": -6.0},
            dropoff={"lat": 53.1, "lon": -6.1},
        )
    )
    second_ride = await runtime.request_ride.execute(
        RequestRideCommand(
            customer_id="customer-2",
            pickup={"lat": 54.0, "lon": -7.0},
            dropoff={"lat": 54.1, "lon": -7.1},
        )
    )
    first_issue = await runtime.issue_submission.execute(
        IssueSubmissionCommand(
            ride_id=first_ride.ride_id,
            customer_id="customer-1",
            category="billing",
            description="question",
        )
    )
    second_issue = await runtime.issue_submission.execute(
        IssueSubmissionCommand(
            ride_id=second_ride.ride_id,
            customer_id="customer-2",
            category="support",
            description="question",
        )
    )

    assert first_ride.ride_id != second_ride.ride_id
    assert first_issue.issue_id != second_issue.issue_id
    assert consumer.subscriptions == [
        "DriverAssigned",
        "EtaUpdated",
        "NoDriverAvailableVisible",
        "PaymentFailedVisible",
        "PaymentAuthorised",
        "PaymentConfirmedVisible",
        "RideCompletedVisible",
        "TripProgressVisible",
    ]

    await runtime.close()

    assert publisher.closed is True
    assert consumer.closed is True
    assert ride_store.closed is True
    assert issue_store.closed is True


@pytest.mark.parametrize(
    ("module_path", "service_name", "expected_topics"),
    [
        (
            "ridenow_driver.bootstrap.app",
            "driver",
            ["DriverSearchRequested", "PaymentAuthorised"],
        ),
        ("ridenow_route.bootstrap.app", "route", ["RouteRequested"]),
        ("ridenow_pricing.bootstrap.app", "pricing", ["FareRequested"]),
        (
            "ridenow_payment.bootstrap.app",
            "payment",
            ["PaymentAuthorisationRequested", "PaymentCaptureRequested"],
        ),
        (
            "ridenow_tracking.bootstrap.app",
            "tracking",
            ["TrackingLocationUpdated", "TrackingLocationUpdated"],
        ),
        (
            "ridenow_notification.bootstrap.app",
            "notification",
            [
                "RideRequested",
                "NoDriverAvailable",
                "DriverAssigned",
                "EtaUpdated",
                "FareEstimated",
                "PaymentFailed",
                "DriverLocationUpdated",
                "TripStatusUpdated",
                "TripCompleted",
                "PaymentCaptured",
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_service_real_runtime_wires_expected_subscriptions(
    monkeypatch: pytest.MonkeyPatch,
    module_path: str,
    service_name: str,
    expected_topics: list[str],
) -> None:
    """Verify each worker service wires its RabbitMQ subscriptions correctly."""

    module = importlib.import_module(module_path)
    publisher = FakePublisher()
    consumer = FakeConsumer()

    async def fake_create_event_publisher(settings: object) -> FakePublisher:
        return publisher

    async def fake_create_event_consumer(settings: object) -> FakeConsumer:
        return consumer

    monkeypatch.setattr(module, "create_event_publisher", fake_create_event_publisher)
    monkeypatch.setattr(module, "create_event_consumer", fake_create_event_consumer)

    runtime = await module.create_real_runtime(
        SharedServiceSettings(service_name=service_name)
    )

    assert consumer.subscriptions == expected_topics

    await runtime.close()

    assert publisher.closed is True
    assert consumer.closed is True


@pytest.mark.parametrize(
    ("module_path", "service_name"),
    [
        ("ridenow_driver.bootstrap.app", "driver"),
        ("ridenow_route.bootstrap.app", "route"),
        ("ridenow_pricing.bootstrap.app", "pricing"),
        ("ridenow_payment.bootstrap.app", "payment"),
        ("ridenow_tracking.bootstrap.app", "tracking"),
        ("ridenow_notification.bootstrap.app", "notification"),
    ],
)
def test_worker_create_app_real_mode_uses_lifespan_runtime(
    monkeypatch: pytest.MonkeyPatch,
    module_path: str,
    service_name: str,
) -> None:
    """Verify worker service apps enter and close their real-mode lifespan."""

    module = importlib.import_module(module_path)

    class FakeRuntime:
        def __init__(self) -> None:
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    runtime = FakeRuntime()

    async def fake_create_real_runtime(settings: SharedServiceSettings) -> FakeRuntime:
        assert settings.service_name == service_name
        return runtime

    monkeypatch.setenv("RIDENOW_RUNTIME_MODE", "real")
    monkeypatch.setenv("RIDENOW_SERVICE_NAME", service_name)
    monkeypatch.setattr(module, "create_real_runtime", fake_create_real_runtime)

    app = module.create_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.json() == {"service": service_name, "status": "ok"}
    assert runtime.closed is True


def test_broker_create_app_real_mode_uses_lifespan_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify the Broker app enters and closes its real-mode lifespan."""

    module = importlib.import_module("ridenow_broker.bootstrap.app")
    runtime = FakeBrokerAppRuntime()

    async def fake_create_real_runtime(
        settings: SharedServiceSettings,
    ) -> FakeBrokerAppRuntime:
        assert settings.service_name == "broker"
        return runtime

    monkeypatch.setenv("RIDENOW_RUNTIME_MODE", "real")
    monkeypatch.setenv("RIDENOW_SERVICE_NAME", "broker")
    monkeypatch.setattr(module, "create_real_runtime", fake_create_real_runtime)

    app = module.create_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.json() == {"service": "broker", "status": "ok"}
    assert runtime.closed is True


@pytest.mark.asyncio
async def test_delayed_event_handler_waits_before_delegating(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify delayed_event_handler sleeps before invoking the handler."""

    recorded_delays: list[float] = []
    received_events: list[object] = []

    async def fake_sleep(delay_seconds: float) -> None:
        recorded_delays.append(delay_seconds)

    async def handler(event: object) -> None:
        received_events.append(event)

    monkeypatch.setattr("ridenow_shared.bootstrap.asyncio.sleep", fake_sleep)

    wrapped = delayed_event_handler(0.25, handler)
    event = object()

    await wrapped(event)

    assert recorded_delays == [0.25]
    assert received_events == [event]


def test_run_service_app_uses_shared_uvicorn_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify run_service_app forwards shared settings into uvicorn.run."""

    captured: dict[str, object] = {}

    def fake_run(app_path: str, **kwargs: object) -> None:
        captured["app_path"] = app_path
        captured["kwargs"] = kwargs

    monkeypatch.setenv("RIDENOW_SERVICE_NAME", "pricing")
    monkeypatch.setattr("ridenow_shared.bootstrap.uvicorn.run", fake_run)

    run_service_app("ridenow_pricing.bootstrap.app", "pricing")

    assert captured["app_path"] == "ridenow_pricing.bootstrap.app:create_app"
    assert captured["kwargs"] == {
        "factory": True,
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
        "access_log": False,
    }
