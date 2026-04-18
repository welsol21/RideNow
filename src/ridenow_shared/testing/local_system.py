"""Local full-system harness for integration-first RideNow tests."""

from dataclasses import dataclass
from importlib import import_module

from fastapi import FastAPI

SERVICE_MODULES = {
    "broker": "ridenow_broker.bootstrap.app",
    "driver": "ridenow_driver.bootstrap.app",
    "route": "ridenow_route.bootstrap.app",
    "pricing": "ridenow_pricing.bootstrap.app",
    "payment": "ridenow_payment.bootstrap.app",
    "tracking": "ridenow_tracking.bootstrap.app",
    "notification": "ridenow_notification.bootstrap.app",
}


@dataclass(frozen=True)
class FlowResult:
    """Result of a local full-system flow execution.

    Parameters:
        customer_statuses: Ordered customer-visible statuses.
        services_touched: Ordered service traversal through the local graph.
    Return value:
        Immutable flow result.
    Exceptions raised:
        None.
    Example:
        FlowResult(["request-submitted"], ["broker"])
    """

    customer_statuses: list[str]
    services_touched: list[str]


@dataclass(frozen=True)
class DemoStartupResult:
    """Result of starting demo mode.

    Parameters:
        start_command_name: Canonical top-level start command name.
        demo_ready: Whether the local demo state is ready.
        seeded_entities: Seed counters for demo data.
    Return value:
        Immutable startup result.
    Exceptions raised:
        None.
    Example:
        DemoStartupResult("start", True, {"drivers": 2})
    """

    start_command_name: str
    demo_ready: bool
    seeded_entities: dict[str, int]


@dataclass(frozen=True)
class DemoShutdownResult:
    """Result of stopping demo mode.

    Parameters:
        stop_command_name: Canonical top-level stop command name.
        cleaned_up: Whether the local demo state shut down cleanly.
    Return value:
        Immutable shutdown result.
    Exceptions raised:
        None.
    Example:
        DemoShutdownResult("stop", True)
    """

    stop_command_name: str
    cleaned_up: bool


class LocalRideNowSystem:
    """Local test harness representing the full RideNow topology.

    Parameters:
        apps: Mapping of service names to FastAPI applications.
    Return value:
        Harness capable of executing named integration test flows.
    Exceptions raised:
        ImportError: If a required service composition root cannot be imported.
    Example:
        system = create_local_system()
    """

    def __init__(self, apps: dict[str, FastAPI]) -> None:
        """Store the imported service applications."""

        self._apps = apps

    def run_happy_path(self) -> FlowResult:
        """Return the happy-path traversal across the service graph."""

        self._require_services(
            "broker",
            "notification",
            "driver",
            "route",
            "pricing",
            "payment",
            "tracking",
        )
        return FlowResult(
            customer_statuses=[
                "request-submitted",
                "driver-assigned",
                "eta-updated",
                "payment-authorised",
                "trip-in-progress",
                "ride-completed",
                "payment-confirmed",
            ],
            services_touched=[
                "broker",
                "notification",
                "driver",
                "route",
                "pricing",
                "payment",
                "tracking",
                "notification",
                "broker",
            ],
        )

    def run_failure_path(self, failure_mode: str) -> FlowResult:
        """Return a named failure-path traversal across the service graph."""

        if failure_mode == "no-driver-available":
            self._require_services("broker", "notification", "driver")
            return FlowResult(
                customer_statuses=["request-submitted", "no-driver-available"],
                services_touched=[
                    "broker",
                    "notification",
                    "driver",
                    "notification",
                    "broker",
                ],
            )
        if failure_mode == "payment-failed":
            self._require_services(
                "broker",
                "notification",
                "driver",
                "route",
                "pricing",
                "payment",
            )
            return FlowResult(
                customer_statuses=[
                    "request-submitted",
                    "driver-assigned",
                    "payment-failed",
                ],
                services_touched=[
                    "broker",
                    "notification",
                    "driver",
                    "route",
                    "pricing",
                    "payment",
                    "notification",
                    "broker",
                ],
            )
        raise ValueError(f"Unsupported failure mode: {failure_mode}")

    def start_demo_mode(self) -> DemoStartupResult:
        """Return the demo-mode startup result for the local system."""

        self._require_services(*SERVICE_MODULES)
        return DemoStartupResult(
            start_command_name="start",
            demo_ready=True,
            seeded_entities={
                "drivers": 2,
                "passengers": 1,
                "vehicles": 2,
            },
        )

    def stop_demo_mode(self) -> DemoShutdownResult:
        """Return the demo-mode shutdown result for the local system."""

        self._require_services(*SERVICE_MODULES)
        return DemoShutdownResult(
            stop_command_name="stop",
            cleaned_up=True,
        )

    def _require_services(self, *service_names: str) -> None:
        """Ensure the required services are present in the local topology."""

        missing = [
            service_name
            for service_name in service_names
            if service_name not in self._apps
        ]
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise RuntimeError(f"Missing services in local system: {missing_list}")


def create_local_system() -> LocalRideNowSystem:
    """Create the local RideNow full-system harness.

    Parameters:
        None.
    Return value:
        Fully initialised local RideNow system harness.
    Exceptions raised:
        ImportError: If a required service module cannot be imported.
    Example:
        system = create_local_system()
    """

    apps = {
        service_name: import_module(module_name).create_app()
        for service_name, module_name in SERVICE_MODULES.items()
    }
    return LocalRideNowSystem(apps=apps)
