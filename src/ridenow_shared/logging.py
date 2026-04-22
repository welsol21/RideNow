"""Structured logging helpers shared across RideNow services."""

from __future__ import annotations

import logging
import sys
from time import perf_counter
from typing import TYPE_CHECKING, TextIO

import structlog

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import FastAPI, Request, Response

_STRUCTURED_LOGGING_CONFIGURED = False


def configure_structured_logging(
    *,
    level: int = logging.INFO,
    stream: TextIO | None = None,
    force: bool = False,
) -> None:
    """Configure process-wide JSON logging for service runtimes and tests."""

    global _STRUCTURED_LOGGING_CONFIGURED

    if _STRUCTURED_LOGGING_CONFIGURED and not force:
        return

    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=stream or sys.stdout,
        force=True,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _STRUCTURED_LOGGING_CONFIGURED = True


def attach_request_logging(app: FastAPI, service_name: str) -> None:
    """Attach structured HTTP request logging to a FastAPI application."""

    logger = structlog.get_logger("http").bind(service=service_name)

    @app.middleware("http")
    async def log_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round((perf_counter() - started_at) * 1000, 2),
            )
            raise

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        return response
