# Data Model

RideNow uses two main data shapes:

- RabbitMQ event envelopes
- Broker-owned JSON state in PostgreSQL

## Event Envelope

All inter-service messages use the shared `EventEnvelope` model:

| Field | Type | Meaning |
| --- | --- | --- |
| `event_id` | `str` | Globally unique event identifier |
| `correlation_id` | `str` | Workflow identifier, usually the `ride_id` |
| `source` | `str` | Emitting service |
| `occurred_at` | `datetime` | UTC emission timestamp |
| `payload.name` | `str` | Domain event name, also used as RabbitMQ routing key |
| `payload.data` | `dict[str, object]` | Event body |

## Broker Ride State

Broker persists customer-visible ride state in PostgreSQL JSONB under
logical store name `broker-ride-status`.

### Core fields

| Field | Type | Meaning |
| --- | --- | --- |
| `customer_id` | `str` | Customer identity from the initial request |
| `status` | `str` | Customer-visible ride status |
| `pickup` | `dict` | Pickup coordinates |
| `dropoff` | `dict` | Dropoff coordinates |
| `driver` | `dict \| null` | Driver and vehicle details |
| `route` | `dict \| null` | Distance, pickup ETA, trip duration |
| `payment` | `dict \| null` | Authorisation and capture details |
| `progress` | `dict \| null` | Trip progress or completion details |

### Status progression

- `request-submitted`
- `driver-assigned`
- `eta-updated`
- `payment-authorised`
- `trip-in-progress`
- `ride-completed`
- `payment-confirmed`

Failure terminal states:

- `no-driver-available`
- `payment-failed`

## Broker Issue State

Broker persists issue submissions in logical store `broker-issue-store`.

| Field | Type |
| --- | --- |
| `ride_id` | `str` |
| `customer_id` | `str` |
| `category` | `str` |
| `description` | `str` |
| `status` | `str` |

## PostgreSQL Physical Storage

The shared PostgreSQL adapter persists data in table `service_state`:

| Column | Type | Notes |
| --- | --- | --- |
| `store_name` | `varchar(120)` | Logical namespace |
| `state_key` | `varchar(200)` | Entity key such as `ride_id` |
| `payload` | `jsonb` | Stored document |

Primary key:

- (`store_name`, `state_key`)

Writes use upsert semantics, so repeated updates replace the JSONB
payload for the same logical key.
