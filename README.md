# RideNow

RideNow is a multi-service ride-hailing platform implemented as a
single repository with seven collaborating services:

- Broker
- Driver
- Route
- Pricing
- Payment
- Tracking
- Notification

## Current State

This repository is being rebuilt from the second implementation attempt
using a stricter prompt that requires:

- full-system integration-first delivery;
- real service-to-service collaboration;
- one-command local start and one-command local stop;
- manual demoability with dummy/demo data.

## Repository Layout

- `services/` - service-specific source trees
- `src/ridenow_shared/` - shared events, contracts, and config
- `tests/` - acceptance, unit, contract, integration, e2e, and non-functional tests
- `infra/` - Compose and Kubernetes assets
- `docs/` - assignment, architecture, operations, and state documents
- `scripts/` - top-level operational scripts

## Bootstrap Tooling

- Python 3.12+
- FastAPI
- RabbitMQ
- PostgreSQL
- pytest

## Next Steps

Follow `PLAN.md`. The project uses outside-in TDD and progresses one
task at a time with a commit after every checked item.
