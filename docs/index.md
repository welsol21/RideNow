# RideNow

RideNow is a seven-service ride-hailing system delivered as a single
repository with a real multi-service runtime. The public API is exposed
by `broker`, while the rest of the services collaborate through RabbitMQ
events and update the customer-visible Broker read model.

## Runtime Topology

- `broker` owns the public API, customer-visible ride state, and issue submission
- `notification` relays domain events between services and emits visible Broker-facing events
- `driver`, `route`, `pricing`, `payment`, and `tracking` execute deterministic domain decisions
- `rabbitmq` is the event backbone
- `postgres` stores Broker state
- `prometheus` scrapes service metrics in the Compose demo stack

## Main Customer Scenarios

- Happy path from `POST /rides` to `payment-confirmed`
- `no-driver-available` failure path
- `payment-failed` failure path
- `POST /issues` acknowledgement
- Broker CLI commands for representative inbound coverage

## Start Here

- Architecture overview: `architecture/overview.md`
- Local demo guide: `guides/running_locally.md`
- Monitoring guide: `operations/monitoring.md`
- Kubernetes demo guide: `guides/kubernetes_demo.md`
