# Acceptance Catalogue

This catalogue maps customer-visible scenarios to the tests that prove
them.

## Acceptance Tests

| Scenario | Test file | Main assertion |
| --- | --- | --- |
| Health check | `tests/acceptance/test_health_check.py` | Broker reports `{"service":"broker","status":"ok"}` |
| Request ride acknowledgement | `tests/acceptance/test_request_ride_acknowledgement.py` | `POST /rides` returns `202` and `request-submitted` |
| Driver assigned | `tests/acceptance/test_driver_assigned.py` | Broker read model reaches `driver-assigned` |
| Route and ETA feedback | `tests/acceptance/test_route_and_eta_feedback.py` | Broker read model includes route payload |
| Payment authorised | `tests/acceptance/test_payment_authorised.py` | Broker read model includes payment authorisation payload |
| Trip progress | `tests/acceptance/test_trip_progress.py` | Broker read model reaches `trip-in-progress` |
| Ride completed and payment confirmed | `tests/acceptance/test_ride_completed_payment_confirmed.py` | Broker reaches `payment-confirmed` |
| No driver available | `tests/acceptance/test_no_driver_available.py` | Broker reaches terminal `no-driver-available` |
| Payment failed | `tests/acceptance/test_payment_failed.py` | Broker reaches terminal `payment-failed` |
| Issue submitted | `tests/acceptance/test_issue_submitted.py` | `POST /issues` returns `issue-submitted` |
| CLI adapter | `tests/acceptance/test_cli_adapter.py` | Broker CLI covers health, request-ride, submit-issue |

## Integration-First Baseline

| Scenario | Test file | Purpose |
| --- | --- | --- |
| Startup and readiness matrix | `tests/integration/test_full_system_startup_readiness.py` | Proves all seven service apps exist and expose probes |
| Happy-path connectivity | `tests/integration/test_full_system_happy_path_connectivity.py` | Proves the full service graph order |
| Failure-path connectivity | `tests/integration/test_full_system_failure_path_connectivity.py` | Proves main failure branches traverse the graph |
| Manual demo mode | `tests/integration/test_manual_demo_mode.py` | Proves one-command demo start/stop contract in the local harness |

## Live Runtime Checks

| Scenario | Test file | Purpose |
| --- | --- | --- |
| Compose happy path | `tests/e2e/test_system_smoke.py` | Live Broker request reaches `payment-confirmed` |
| Compose service probes | `tests/e2e/test_service_probes.py` | All seven HTTP services expose health and readiness |

## Non-Functional Checks

| Scenario | Test file | Purpose |
| --- | --- | --- |
| Performance | `tests/nonfunctional/test_broker_performance.py` | Load and latency envelope |
| Resilience | `tests/nonfunctional/test_broker_resilience.py` | Broker restart and readiness recovery |
| Dependency audit | `tests/nonfunctional/test_dependency_audit.py` | Runtime dependency vulnerability check |
| Soak scaffold | `tests/nonfunctional/test_broker_soak.py` | Short reliability scaffold |
| Monitoring validation | `tests/nonfunctional/test_monitoring_validation.py` | Prometheus and `/metrics` verification |
