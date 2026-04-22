"""Unit tests for shared async retry behaviour."""

import pytest

from ridenow_shared.retry import retry_async


@pytest.mark.asyncio
async def test_retry_async_retries_until_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify retry_async keeps retrying until the operation succeeds."""

    sleep_calls: list[float] = []

    async def fake_sleep(delay_seconds: float) -> None:
        sleep_calls.append(delay_seconds)

    monkeypatch.setattr("ridenow_shared.retry.asyncio.sleep", fake_sleep)
    attempts = 0

    async def flaky_operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("not ready")
        return "ready"

    result = await retry_async(flaky_operation, attempts=3, delay_seconds=0.25)

    assert result == "ready"
    assert sleep_calls == [0.25, 0.25]


@pytest.mark.asyncio
async def test_retry_async_re_raises_when_attempts_are_exhausted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify retry_async re-raises the final error after the last attempt."""

    sleep_calls: list[float] = []

    async def fake_sleep(delay_seconds: float) -> None:
        sleep_calls.append(delay_seconds)

    monkeypatch.setattr("ridenow_shared.retry.asyncio.sleep", fake_sleep)

    async def failing_operation() -> str:
        raise RuntimeError("still not ready")

    with pytest.raises(RuntimeError, match="still not ready"):
        await retry_async(failing_operation, attempts=3, delay_seconds=0.1)

    assert sleep_calls == [0.1, 0.1]
