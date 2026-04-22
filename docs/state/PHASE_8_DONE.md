# Phase 8 Done

## Scope Closed

- performance/load validation for repeated ride submissions
- resilience check for Broker recovery after Compose restart
- runtime dependency audit with a pinned runtime manifest
- short soak-style reliability scaffold
- monitoring validation through Prometheus and Broker metrics

## Validation

- `.\.venv\Scripts\python.exe -m pytest -q tests/nonfunctional`
- `.\.venv\Scripts\python.exe -m ruff check src services tests`
- `.\.venv\Scripts\python.exe -m mypy src services tests/nonfunctional`
- `.\.venv\Scripts\python.exe -m pytest -q tests/unit tests/acceptance tests/contracts tests/integration tests/e2e tests/nonfunctional`
- `docker compose -f infra\compose\docker-compose.yml up -d --build`
- `.\.venv\Scripts\python.exe -m pip_audit -r requirements-runtime.txt --cache-dir .tmp-pip-audit-cache --progress-spinner off`

## Outcome

- `5 passed` in the dedicated nonfunctional suite
- `97 passed` in the full regression suite
- runtime dependency audit is green after upgrading to `fastapi==0.135.3` and `starlette==0.49.1`
- Broker recovers after container restart and monitoring remains healthy through Prometheus
