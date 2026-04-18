"""Shared bootstrap helpers for simple service composition roots."""

from fastapi import FastAPI


def create_probe_app(service_name: str) -> FastAPI:
    """Create a minimal FastAPI app exposing health and readiness probes.

    Parameters:
        service_name: Logical name of the service application.
    Return value:
        Configured FastAPI application exposing `/health` and `/ready`.
    Exceptions raised:
        None.
    Example:
        app = create_probe_app("driver")
    """

    app = FastAPI(title=f"RideNow {service_name.title()}", version="0.1.0")

    @app.get("/health")
    def health_check() -> dict[str, str]:
        """Return the health probe payload."""

        return {
            "service": service_name,
            "status": "ok",
        }

    @app.get("/ready")
    def readiness_check() -> dict[str, str]:
        """Return the readiness probe payload."""

        return {
            "service": service_name,
            "status": "ready",
        }

    return app
