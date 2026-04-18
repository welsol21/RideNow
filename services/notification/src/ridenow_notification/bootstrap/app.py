"""Notification service composition root for startup/readiness wiring."""

from fastapi import FastAPI

from ridenow_shared import create_probe_app


def create_app() -> FastAPI:
    """Create the Notification FastAPI application."""

    return create_probe_app("notification")
