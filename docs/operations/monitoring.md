# Monitoring

RideNow exposes structured logs and Prometheus metrics for all services.

## Metrics

Every FastAPI app exposes:

- `GET /metrics`

Main custom metrics:

| Metric | Type | Labels |
| --- | --- | --- |
| `ridenow_http_requests_total` | Counter | `service`, `method`, `path`, `status_code` |
| `ridenow_http_request_duration_seconds` | Histogram | `service`, `method`, `path` |

Compose Prometheus config:

- `infra/compose/prometheus.yml`

Prometheus UI:

- `http://127.0.0.1:9090`

Useful query:

```text
up
```

Expected Compose result:

- `broker = 1`
- `driver = 1`
- `route = 1`
- `pricing = 1`
- `payment = 1`
- `tracking = 1`
- `notification = 1`

## Structured Logs

All HTTP services configure JSON logging through `src/ridenow_shared/logging.py`.

Log characteristics:

- JSON lines to stdout
- ISO UTC timestamps
- service name bound into the event
- request method, path, status code, duration

Important log events:

- `http_request`
- `http_request_failed`

Example inspection:

```powershell
docker compose -f infra/compose/docker-compose.yml logs broker
```

## Probe Endpoints

Every service exposes:

- `/health`
- `/ready`
- `/metrics`

These probes are validated by:

- `tests/e2e/test_service_probes.py`
- `tests/nonfunctional/test_monitoring_validation.py`

## Monitoring Scope

- Compose includes Prometheus
- Kubernetes manifests currently cover the core services and dependencies
- Prometheus is not yet deployed as part of the Kubernetes manifest set
