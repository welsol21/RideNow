# Service Catalogue

This document identifies the implementation scope of each microservice.

## Summary

| Service | Primary responsibility | Inbound surface | Outbound surface | Persistent state |
| --- | --- | --- | --- | --- |
| Broker | Public API and customer-visible ride state | HTTP, CLI | RabbitMQ publish/consume, PostgreSQL state store | Yes |
| Driver | Driver assignment and location emission | RabbitMQ consume | RabbitMQ publish | No |
| Route | Route and ETA calculation | RabbitMQ consume | RabbitMQ publish | No |
| Pricing | Fare estimation | RabbitMQ consume | RabbitMQ publish | No |
| Payment | Payment authorisation and capture | RabbitMQ consume | RabbitMQ publish | No |
| Tracking | Trip progress and trip completion | RabbitMQ consume | RabbitMQ publish | No |
| Notification | Relay, fan-out, and visible-event projection | RabbitMQ consume | RabbitMQ publish | No |

## Broker

- Implements:
  - `POST /rides`
  - `GET /rides/{ride_id}`
  - `POST /issues`
  - `GET /health`, `GET /ready`, `GET /metrics`
  - CLI commands `health`, `request-ride`, `submit-issue`
- Owns:
  - customer-visible ride lifecycle
  - issue acknowledgement
  - PostgreSQL stores `broker-ride-status` and `broker-issue-store`
- Consumes:
  - `DriverAssigned`
  - `EtaUpdated`
  - `PaymentAuthorised`
  - `TripProgressVisible`
  - `RideCompletedVisible`
  - `PaymentConfirmedVisible`
  - `NoDriverAvailableVisible`
  - `PaymentFailedVisible`
- Publishes:
  - `RideRequested`
  - `IssueSubmitted`

## Driver

- Implements:
  - driver assignment decision
  - deterministic no-driver branch
  - driver location emission after payment authorisation
- Consumes:
  - `DriverSearchRequested`
  - `PaymentAuthorised`
- Publishes:
  - `DriverAssigned`
  - `NoDriverAvailable`
  - `DriverLocationUpdated`

## Route

- Implements deterministic route calculation for the demo workflow
- Consumes:
  - `RouteRequested`
- Publishes:
  - `EtaUpdated`

## Pricing

- Implements deterministic fare calculation for the demo workflow
- Consumes:
  - `FareRequested`
- Publishes:
  - `FareEstimated`

## Payment

- Implements payment authorisation and capture
- Supports deterministic failure for `customer-payment-fail`
- Consumes:
  - `PaymentAuthorisationRequested`
  - `PaymentCaptureRequested`
- Publishes:
  - `PaymentAuthorised`
  - `PaymentFailed`
  - `PaymentCaptured`

## Tracking

- Implements trip progress and trip completion
- Consumes:
  - `TrackingLocationUpdated`
- Publishes:
  - `TripStatusUpdated`
  - `TripCompleted`

## Notification

- Implements the relay layer between services and Broker-visible events
- Consumes:
  - `RideRequested`
  - `NoDriverAvailable`
  - `DriverAssigned`
  - `EtaUpdated`
  - `FareEstimated`
  - `PaymentFailed`
  - `DriverLocationUpdated`
  - `TripStatusUpdated`
  - `TripCompleted`
  - `PaymentCaptured`
- Publishes:
  - `DriverSearchRequested`
  - `NoDriverAvailableVisible`
  - `RouteRequested`
  - `FareRequested`
  - `PaymentAuthorisationRequested`
  - `PaymentFailedVisible`
  - `TrackingLocationUpdated`
  - `TripProgressVisible`
  - `RideCompletedVisible`
  - `PaymentCaptureRequested`
  - `PaymentConfirmedVisible`
