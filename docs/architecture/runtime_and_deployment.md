# Runtime and Deployment

RideNow supports two main deployment targets:

- local Docker Compose
- Kubernetes via `kubectl apply -k infra/kubernetes`

## Compose Runtime

Compose file:

- `infra/compose/docker-compose.yml`

Services:

| Service | Host port | Notes |
| --- | --- | --- |
| `broker` | `8001` | Public API |
| `driver` | `8002` | Probe and metrics only |
| `route` | `8003` | Probe and metrics only |
| `pricing` | `8004` | Probe and metrics only |
| `payment` | `8005` | Probe and metrics only |
| `tracking` | `8006` | Probe and metrics only |
| `notification` | `8007` | Probe and metrics only |
| `rabbitmq` | `5672`, `15672` | AMQP and management UI |
| `postgres` | `15432` | Host-mapped to avoid local `5432` conflicts |
| `prometheus` | `9090` | Monitoring UI and API |

Start:

```powershell
docker compose -f infra/compose/docker-compose.yml up -d --build
```

Stop:

```powershell
docker compose -f infra/compose/docker-compose.yml down -v
```

## Kubernetes Runtime

Kubernetes manifests live in `infra/kubernetes/` and include:

- namespace
- RabbitMQ
- PostgreSQL
- seven service deployments and ClusterIP services

Apply:

```powershell
kubectl apply -k infra/kubernetes
```

Delete:

```powershell
kubectl delete -k infra/kubernetes
```

## Shared Environment Variables

| Variable | Purpose |
| --- | --- |
| `RIDENOW_RUNTIME_MODE` | `local` or `real` |
| `RIDENOW_SERVICE_NAME` | service identity used in logs and settings |
| `RIDENOW_HTTP_PORT` | FastAPI bind port |
| `RIDENOW_RABBITMQ_URL` | AMQP connection URL |
| `RIDENOW_POSTGRES_URL` | SQLAlchemy async PostgreSQL URL |
| `RIDENOW_RABBITMQ_EXCHANGE` | exchange name, defaults to `ridenow.events` |
| `RIDENOW_RABBITMQ_PREFETCH_COUNT` | consumer prefetch count |

## Runtime Modes

- `broker`
  - `local`: in-memory full graph used by acceptance tests and CLI
  - `real`: RabbitMQ + PostgreSQL runtime used by Compose and Kubernetes
- other services
  - `local`: probe-only app for early integration baseline
  - `real`: RabbitMQ-backed consumer/publisher runtime with probes and metrics

## Deployment Notes

- Broker is the only public business API
- All services expose `/health`, `/ready`, and `/metrics`
- Prometheus is part of the Compose stack only in the current scope
