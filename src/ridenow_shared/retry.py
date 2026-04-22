"""Async retry helpers shared by infrastructure adapters."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

ResultT = TypeVar("ResultT")


async def retry_async(
    operation: Callable[[], Awaitable[ResultT]],
    *,
    attempts: int = 20,
    delay_seconds: float = 0.5,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
) -> ResultT:
    """Retry an async operation a bounded number of times before re-raising."""

    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except retry_on as error:
            last_error = error
            if attempt == attempts:
                raise
            await asyncio.sleep(delay_seconds)

    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_async exhausted without returning or raising")
