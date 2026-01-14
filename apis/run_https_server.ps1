#!/usr/bin/env pwsh
# Simple HTTPS Django server startup for Face Recognition app
# No external dependencies required beyond Django

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Face Recognition Server - HTTPS Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if certs exist
if (-not (Test-Path "certs\localhost.crt") -or -not (Test-Path "certs\localhost.key")) {
    Write-Host "Generating SSL certificates..." -ForegroundColor Yellow
    python generate_cert.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to generate certificates!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting HTTPS server..." -ForegroundColor Cyan
Write-Host ""

# Run the HTTPS server
python run_https.py

Read-Host "Press Enter to exit"

