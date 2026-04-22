# Kubernetes Demo

This guide runs the RideNow core stack on a local Kubernetes cluster.

## Prerequisites

- A working Kubernetes context
- `kubectl`
- Local images built from the repository if the cluster does not pull them remotely

## Apply the Manifests

```powershell
kubectl apply -k infra/kubernetes
```

## Check the Namespace

```powershell
kubectl -n ridenow get pods,svc
```

Wait until Broker, RabbitMQ, PostgreSQL, Notification, Driver, Route,
Pricing, Payment, and Tracking are ready.

## Port-Forward Broker

```powershell
kubectl -n ridenow port-forward svc/broker 8001:8001
```

In a second terminal:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/health"
Invoke-RestMethod "http://127.0.0.1:8001/ready"
```

## Run a Demo Ride

```powershell
$body = @{
  customer_id = "customer-demo"
  pickup = @{
    lat = 53.3498
    lon = -6.2603
  }
  dropoff = @{
    lat = 53.3440
    lon = -6.2672
  }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8001/rides" `
  -ContentType "application/json" `
  -Body $body

$response
```

Poll:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/rides/<ride_id>"
```

## Inspect Logs

```powershell
kubectl -n ridenow logs deploy/broker -f
kubectl -n ridenow logs deploy/notification -f
kubectl -n ridenow logs deploy/payment -f
```

## Tear Down

```powershell
kubectl delete -k infra/kubernetes
```
