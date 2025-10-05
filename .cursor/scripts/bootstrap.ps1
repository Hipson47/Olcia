#!/usr/bin/env pwsh

# Windows-first MCP+RAG Bootstrap Script
# Sets up Python virtual environment and installs dependencies

param(
    [string]$VenvPath = "venv",
    [switch]$Force
)

Write-Host "🚀 Bootstrapping MCP+RAG environment..." -ForegroundColor Green

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Poetry installation
try {
    $poetryVersion = poetry --version 2>&1
    Write-Host "✅ Poetry found: $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Poetry not found. Please install Poetry from https://python-poetry.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (Test-Path $VenvPath) {
    if ($Force) {
        Write-Host "🔄 Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VenvPath
    } else {
        Write-Host "⚠️  Virtual environment already exists at '$VenvPath'. Use -Force to recreate." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "📦 Creating virtual environment at '$VenvPath'..." -ForegroundColor Blue
python -m venv $VenvPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& "$VenvPath\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Generate/update poetry.lock if needed
Write-Host "🔒 Ensuring poetry.lock is up to date..." -ForegroundColor Blue
poetry lock --no-update

# Install dependencies with Poetry
Write-Host "📚 Installing dependencies with Poetry..." -ForegroundColor Blue
poetry install --no-interaction --no-ansi

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "🔍 Verifying installation..." -ForegroundColor Blue
try {
    python -c "import chromadb, mcp; print('✅ Core dependencies installed successfully')"
} catch {
    Write-Host "❌ Core dependencies verification failed" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Bootstrap complete! Virtual environment ready at '$VenvPath'" -ForegroundColor Green
Write-Host "💡 To activate in future sessions: & '$VenvPath\Scripts\Activate.ps1'" -ForegroundColor Cyan
