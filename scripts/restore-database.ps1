# Restore Predico database: Docker up, migrations, World Cup seed data.
# Prerequisites: Docker Desktop running (whale icon steady, not "starting").
$ErrorActionPreference = "Stop"

$Docker = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$Compose = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Root "docker-compose.yml"))) {
    $Root = "c:\Projects\predico"
}

Set-Location $Root

Write-Host "Checking Docker daemon..."
$svc = Get-Service com.docker.service -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -ne "Running") {
    Write-Warning "com.docker.service is $($svc.Status). Try: open Docker Desktop, or run PowerShell as Administrator and: Start-Service com.docker.service"
}
$job = Start-Job { param($d) & $d info --format "{{.ServerVersion}}" 2>&1 } -ArgumentList $Docker
Wait-Job $job -Timeout 30 | Out-Null
if ($job.State -eq "Running") {
    Stop-Job $job; Remove-Job $job
    Write-Error @"
Docker daemon is not responding. Please:
  1. Open Docker Desktop from the Start menu and wait until fully started
  2. If it stays stuck: Settings -> Troubleshoot -> Restart Docker Desktop
  3. Or in Admin PowerShell: Start-Service com.docker.service
  4. Run this script again: .\scripts\restore-database.ps1
"@
}
$version = Receive-Job $job
Remove-Job $job
Write-Host "Docker OK (server $version)"

Write-Host "`nStarting services..."
& $Compose compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

Write-Host "Waiting for Postgres..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    $out = & $Compose compose exec -T postgres pg_isready -U predico_user 2>&1
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ready) { throw "Postgres did not become ready in time" }

Write-Host "`nApplying migrations..."
& $Compose compose exec -T backend alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw "alembic upgrade failed" }

Write-Host "`nSeeding World Cup data..."
& $Compose compose exec -T backend python scripts/populate_world_cup_data.py
if ($LASTEXITCODE -ne 0) { throw "populate script failed" }

Write-Host "`nVerifying tables..."
& $Compose compose exec -T postgres psql -U predico_user -d predico_db -c "\dt"

Write-Host "`nDone. Backend: http://localhost:8000  |  Frontend: cd frontend && npm run dev"
