$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$composeFile = Join-Path $repoRoot "infra\compose\docker-compose.yml"
$dockerConfig = Join-Path $repoRoot ".tmp-docker-config"
New-Item -ItemType Directory -Force -Path $dockerConfig | Out-Null
$env:DOCKER_CONFIG = $dockerConfig

function Wait-ForTcpPort {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HostName,
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [Parameter(Mandatory = $true)]
        [datetime]$Deadline
    )

    while ((Get-Date) -lt $Deadline) {
        $client = $null
        try {
            $client = [System.Net.Sockets.TcpClient]::new()
            $asyncResult = $client.BeginConnect($HostName, $Port, $null, $null)
            if ($asyncResult.AsyncWaitHandle.WaitOne(1000) -and $client.Connected) {
                $client.EndConnect($asyncResult)
                return
            }
        }
        catch {
        }
        finally {
            if ($null -ne $client) {
                $client.Dispose()
            }
        }
        Start-Sleep -Milliseconds 500
    }

    throw ("TCP endpoint {0}:{1} did not become ready in time." -f $HostName, $Port)
}

Write-Host "Starting RideNow demo stack..."
docker compose -f $composeFile up -d rabbitmq postgres
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed."
}

$infraDeadline = (Get-Date).AddSeconds(60)
Wait-ForTcpPort -HostName "127.0.0.1" -Port 5672 -Deadline $infraDeadline
Wait-ForTcpPort -HostName "127.0.0.1" -Port 15432 -Deadline $infraDeadline

docker compose -f $composeFile up -d --build broker driver route pricing payment tracking notification prometheus
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed."
}

$services = @(
    @{ Name = "broker"; Port = 8001 },
    @{ Name = "driver"; Port = 8002 },
    @{ Name = "route"; Port = 8003 },
    @{ Name = "pricing"; Port = 8004 },
    @{ Name = "payment"; Port = 8005 },
    @{ Name = "tracking"; Port = 8006 },
    @{ Name = "notification"; Port = 8007 }
)

$deadline = (Get-Date).AddSeconds(90)
foreach ($service in $services) {
    $ready = $false
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-RestMethod -Uri ("http://127.0.0.1:{0}/ready" -f $service.Port)
            if ($response.status -eq "ready") {
                $ready = $true
                break
            }
        }
        catch {
            Start-Sleep -Milliseconds 500
            continue
        }
        Start-Sleep -Milliseconds 500
    }

    if (-not $ready) {
        throw ("Service '{0}' did not become ready in time." -f $service.Name)
    }
}

Write-Host ""
Write-Host "RideNow is demo-ready."
Write-Host "Broker API: http://127.0.0.1:8001"
Write-Host "Prometheus: http://127.0.0.1:9090"
Write-Host "RabbitMQ UI: http://127.0.0.1:15672"
Write-Host ""
Write-Host "Demo customer ids:"
Write-Host "  customer-demo            -> happy path"
Write-Host "  customer-no-driver       -> no-driver-available"
Write-Host "  customer-payment-fail    -> payment-failed"
