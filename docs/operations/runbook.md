# Runbook

This runbook covers the most common local and Kubernetes operational
tasks.

## Local Stack Lifecycle

Start:

```powershell
docker compose -f infra/compose/docker-compose.yml up -d --build
```

Stop:

```powershell
docker compose -f infra/compose/docker-compose.yml down -v
```

Inspect status:

```powershell
docker compose -f infra/compose/docker-compose.yml ps
```

Follow logs:

```powershell
docker compose -f infra/compose/docker-compose.yml logs -f broker
docker compose -f infra/compose/docker-compose.yml logs -f notification
```

## Health Checks

Broker:

```powershell
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/ready
curl http://127.0.0.1:8001/metrics
```

All services expose the same probe pattern on ports `8001` to `8007`.

## RabbitMQ

- AMQP: `amqp://guest:guest@localhost:5672/`
- Management UI: `http://127.0.0.1:15672`
- Default credentials: `guest / guest`

Use RabbitMQ UI to confirm exchange `ridenow.events` and transient
consumer queues.

## PostgreSQL

- Host connection: `127.0.0.1:15432`
- Database: `ridenow`
- User: `postgres`
- Password: `postgres`

Broker state is stored in `service_state`.

## Kubernetes

Apply:

```powershell
kubectl apply -k infra/kubernetes
```

Check pods:

```powershell
kubectl -n ridenow get pods,svc
```

Tail Broker logs:

```powershell
kubectl -n ridenow logs deploy/broker -f
```

Remove:

```powershell
kubectl delete -k infra/kubernetes
```

## Failure Triage

If Broker does not progress rides:

1. Check Broker readiness.
2. Check RabbitMQ is reachable.
3. Check Notification is healthy.
4. Check Broker and Notification logs for event flow gaps.
5. Check Prometheus target health if using Compose.

If Broker start fails after prior runs:

1. Inspect `docker compose ps`
2. Inspect `docker compose logs broker postgres rabbitmq`
3. If necessary, reset with `docker compose down -v` and start again
