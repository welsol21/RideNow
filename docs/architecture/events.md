# Events

RideNow uses a durable RabbitMQ topic exchange named
`ridenow.events`. Each event is published with `payload.name` as the
routing key.

## Event Catalogue

| Event | Producer | Consumer | Purpose |
| --- | --- | --- | --- |
| `RideRequested` | Broker | Notification | Start ride workflow |
| `DriverSearchRequested` | Notification | Driver | Ask Driver service to assign |
| `DriverAssigned` | Driver | Broker, Notification | Publish successful assignment |
| `NoDriverAvailable` | Driver | Notification | Publish failed driver search |
| `NoDriverAvailableVisible` | Notification | Broker | Update customer-visible failure |
| `RouteRequested` | Notification | Route | Ask for route and ETA |
| `EtaUpdated` | Route | Broker, Notification | Publish route feedback |
| `FareRequested` | Notification | Pricing | Ask for fare |
| `FareEstimated` | Pricing | Notification | Publish fare estimate |
| `PaymentAuthorisationRequested` | Notification | Payment | Ask Payment to authorise |
| `PaymentAuthorised` | Payment | Broker, Driver | Confirm authorisation |
| `PaymentFailed` | Payment | Notification | Publish failed authorisation |
| `PaymentFailedVisible` | Notification | Broker | Update customer-visible payment failure |
| `DriverLocationUpdated` | Driver | Notification | Publish deterministic driver location |
| `TrackingLocationUpdated` | Notification | Tracking | Ask Tracking to derive progress |
| `TripStatusUpdated` | Tracking | Notification | Publish progress status |
| `TripProgressVisible` | Notification | Broker | Update customer-visible progress |
| `TripCompleted` | Tracking | Notification | Publish ride completion |
| `RideCompletedVisible` | Notification | Broker | Update customer-visible completion |
| `PaymentCaptureRequested` | Notification | Payment | Ask Payment to capture |
| `PaymentCaptured` | Payment | Notification | Publish capture success |
| `PaymentConfirmedVisible` | Notification | Broker | Update customer-visible final payment status |
| `IssueSubmitted` | Broker | none in current scope | Persisted issue acknowledgement event |

## Happy Path

1. `RideRequested`
2. `DriverSearchRequested`
3. `DriverAssigned`
4. `RouteRequested`
5. `EtaUpdated`
6. `FareRequested`
7. `FareEstimated`
8. `PaymentAuthorisationRequested`
9. `PaymentAuthorised`
10. `DriverLocationUpdated`
11. `TrackingLocationUpdated`
12. `TripStatusUpdated`
13. `TripProgressVisible`
14. `TripCompleted`
15. `RideCompletedVisible`
16. `PaymentCaptureRequested`
17. `PaymentCaptured`
18. `PaymentConfirmedVisible`

## Failure Paths

### No driver available

1. `RideRequested`
2. `DriverSearchRequested`
3. `NoDriverAvailable`
4. `NoDriverAvailableVisible`

### Payment failed

1. `RideRequested`
2. `DriverSearchRequested`
3. `DriverAssigned`
4. `RouteRequested`
5. `EtaUpdated`
6. `FareRequested`
7. `FareEstimated`
8. `PaymentAuthorisationRequested`
9. `PaymentFailed`
10. `PaymentFailedVisible`

## Correlation Model

- Ride workflow events use `ride_id` as `correlation_id`
- Issue submission uses `issue_id` as `correlation_id`
- Consumer handlers validate the shared `EventEnvelope` model before
  executing use cases
