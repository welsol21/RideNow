# Phase 6 Done

## Scope Closed

- real RabbitMQ publisher and consumer adapters
- real PostgreSQL state-store adapter
- Compose runtime wiring for all seven services against RabbitMQ and PostgreSQL
- Kubernetes manifests for the full multi-service topology
- live acceptance coverage against the real Broker HTTP surface
- startup retry hardening for brokered infrastructure dependencies

## Validation

- `.\.venv\Scripts\python.exe -m ruff check src services tests`
- `.\.venv\Scripts\python.exe -m mypy src services`
- `.\.venv\Scripts\python.exe -m pytest -q tests/unit tests/acceptance tests/contracts tests/integration`
- `RIDENOW_ACCEPTANCE_MODE=live RIDENOW_BROKER_BASE_URL=http://127.0.0.1:8001 .\.venv\Scripts\python.exe -m pytest -q tests/acceptance/test_health_check.py tests/acceptance/test_request_ride_acknowledgement.py tests/acceptance/test_driver_assigned.py tests/acceptance/test_route_and_eta_feedback.py tests/acceptance/test_payment_authorised.py tests/acceptance/test_trip_progress.py tests/acceptance/test_ride_completed_payment_confirmed.py tests/acceptance/test_no_driver_available.py tests/acceptance/test_payment_failed.py tests/acceptance/test_issue_submitted.py`
- `kubectl kustomize infra\kubernetes`
- `docker compose -f infra\compose\docker-compose.yml ps`

## Outcome

- `66 passed` for local `unit + acceptance + contracts + integration`
- `10 passed` for live HTTP acceptance against the Compose stack
- all nine services remain up under Compose after startup sequencing
- Kubernetes manifests render the full RideNow service topology
