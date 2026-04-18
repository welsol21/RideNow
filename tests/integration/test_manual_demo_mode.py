"""Manual demo-mode integration slice for the local RideNow system."""

import pytest

from ridenow_shared.testing.local_system import create_local_system


@pytest.mark.integration
def test_manual_demo_mode_is_demo_ready_after_one_command_start() -> None:
    """Verify demo mode becomes ready with seed data after one-command startup."""

    system = create_local_system()

    startup = system.start_demo_mode()

    assert startup.start_command_name == "start"
    assert startup.demo_ready is True
    assert startup.seeded_entities["drivers"] >= 1
    assert startup.seeded_entities["passengers"] >= 1
    assert startup.seeded_entities["vehicles"] >= 1

    shutdown = system.stop_demo_mode()

    assert shutdown.stop_command_name == "stop"
    assert shutdown.cleaned_up is True
