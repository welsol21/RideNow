$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$composeFile = Join-Path $repoRoot "infra\compose\docker-compose.yml"
$dockerConfig = Join-Path $repoRoot ".tmp-docker-config"
New-Item -ItemType Directory -Force -Path $dockerConfig | Out-Null
$env:DOCKER_CONFIG = $dockerConfig

Write-Host "Stopping RideNow demo stack..."
docker compose -f $composeFile down -v
if ($LASTEXITCODE -ne 0) {
    throw "docker compose down failed."
}
Write-Host "RideNow stack stopped."
