"""Security-oriented dependency audit validation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.nonfunctional
def test_runtime_dependencies_have_no_known_vulnerabilities() -> None:
    """Verify pinned runtime dependencies pass pip-audit."""

    requirements_file = Path(__file__).resolve().parents[2] / "requirements-runtime.txt"
    audit_cache_dir = Path(__file__).resolve().parents[2] / ".tmp-pip-audit-cache"
    audit_temp_dir = Path(__file__).resolve().parents[2] / ".tmp-pip-audit-temp"
    audit_cache_dir.mkdir(parents=True, exist_ok=True)
    audit_temp_dir.mkdir(parents=True, exist_ok=True)
    python_executable = (
        Path(__file__).resolve().parents[2] / ".venv" / "Scripts" / "python.exe"
    )
    environment = dict(os.environ)
    environment["TMPDIR"] = str(audit_temp_dir)
    environment["TMP"] = str(audit_temp_dir)
    environment["TEMP"] = str(audit_temp_dir)
    completed = subprocess.run(
        [
            str(python_executable),
            "-m",
            "pip_audit",
            "-r",
            str(requirements_file),
            "--progress-spinner",
            "off",
            "--cache-dir",
            str(audit_cache_dir),
        ],
        capture_output=True,
        env=environment,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
