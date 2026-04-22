# Final Report

## Outcome

RideNow is delivered as a working seven-service system with:

- real multi-service collaboration across `broker`, `driver`, `route`,
  `pricing`, `payment`, `tracking`, and `notification`
- one-command local startup via `scripts/start.ps1`
- one-command local shutdown via `scripts/stop.ps1`
- documentation site build through MkDocs
- Compose and Kubernetes deployment assets

## Fresh-Clone Verification

Verification was performed from a clean clone at `turnkey-fresh-clone/`.

Steps executed:

1. Create Python 3.12 virtual environment
2. Install `.[dev,docs,nonfunctional]`
3. Build docs with `mkdocs build --strict`
4. Run `ruff check src services tests`
5. Run `mypy src services tests/nonfunctional`
6. Run test suites
7. Start the full Compose stack with `.\scripts\start.ps1`
8. Stop the Compose stack with `.\scripts\stop.ps1`

## Fresh-Clone Results

- `mkdocs build --strict` succeeded
- `ruff check src services tests` succeeded
- `mypy src services tests/nonfunctional` succeeded
- `pytest -q tests/unit tests/acceptance` -> `63 passed`
- `pytest -q tests/contracts tests/integration` -> `21 passed`
- `pytest -q tests/e2e tests/nonfunctional` -> `13 passed`

## Compose Workflow

Validated from the fresh clone:

- `.\scripts\start.ps1`
  - starts RabbitMQ and PostgreSQL first
  - waits for infrastructure readiness
  - builds and starts all seven application services
  - waits for `/ready` across all services
  - prints demo endpoints and customer ids
- `.\scripts\stop.ps1`
  - cleanly stops the full Compose stack
  - removes the Compose volume and network

## Kubernetes Validation

Validation was performed against local context `kind-ridenow-k8s`.

Steps executed:

1. Load current `compose-*` images into `kind`
2. `kubectl apply -k infra/kubernetes`
3. Wait for pods and services to become ready
4. Port-forward `svc/broker`
5. Verify `GET /health` returns `{"service":"broker","status":"ok"}`

Observed cluster state:

- all application pods reached `1/1 Running`
- RabbitMQ and PostgreSQL reached `1/1 Running`
- all service objects were present for the seven services

## Environment Notes

Two host-environment constraints were observed on this Windows machine:

- Docker engine access from subprocess-based tests requires elevated host access
- direct access to the user kubeconfig file also requires elevated host access

These constraints were handled during verification by running the
relevant commands outside the sandbox. They do not change the repository
artifacts or the service topology.
