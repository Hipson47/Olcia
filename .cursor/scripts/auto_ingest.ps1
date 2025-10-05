#!/usr/bin/env pwsh

# Auto-Ingestion Watcher for RAG System
# Windows PowerShell script to monitor knowledge/ directory and trigger re-ingestion

param(
    [string]$ConfigPath = "$PSScriptRoot/../rag/config.yaml",
    [string]$WatchDirectory = "$PSScriptRoot/../knowledge",
    [int]$DebounceSeconds = 2,
    [switch]$Verbose,
    [switch]$OneShot
)

# Setup logging
$LogLevel = if ($Verbose) { "DEBUG" } else { "INFO" }
$LogFormat = "{0:yyyy-MM-dd HH:mm:ss} [{1}] {2}" -f (Get-Date), $LogLevel, "{0}"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp [$Level] $Message"
    Write-Host $logMessage

    # Also log to file if configured
    $logFile = "$PSScriptRoot/../rag_ingest.log"
    $logMessage | Out-File -FilePath $logFile -Append -Encoding UTF8
}

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python found: $pythonVersion"
        return $true
    } catch {
        Write-Log "Python not found. Please install Python 3.8+ from https://python.org" "ERROR"
        return $false
    }
}

function Test-VirtualEnvironment {
    try {
        # Check if we're in a virtual environment
        $venvActivate = "$PSScriptRoot/../venv/Scripts/Activate.ps1"
        if (Test-Path $venvActivate) {
            Write-Log "Virtual environment found at: $venvActivate"
            return $true
        } else {
            Write-Log "Virtual environment not found. Run scripts/bootstrap.ps1 first" "WARN"
            return $false
        }
    } catch {
        Write-Log "Error checking virtual environment: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Invoke-RAGIngestion {
    param([string[]]$Paths)

    Write-Log "Starting RAG ingestion for paths: $($Paths -join ', ')"

    try {
        # Activate virtual environment
        $venvActivate = "$PSScriptRoot/../venv/Scripts/Activate.ps1"
        if (Test-Path $venvActivate) {
            & $venvActivate
        }

        # Build python command
        $pythonCmd = "python"
        $ingestScript = "$PSScriptRoot/../rag/ingest.py"
        $args = @("--paths") + $Paths

        if ($Verbose) {
            $args += "--verbose"
        }

        Write-Log "Running: $pythonCmd $ingestScript $($args -join ' ')"

        # Execute ingestion
        $startTime = Get-Date
        & $pythonCmd $ingestScript @args
        $exitCode = $LASTEXITCODE
        $duration = (Get-Date) - $startTime

        if ($exitCode -eq 0) {
            Write-Log "Ingestion completed successfully in $($duration.TotalSeconds) seconds"
        } else {
            Write-Log "Ingestion failed with exit code: $exitCode" "ERROR"
        }

        return $exitCode -eq 0

    } catch {
        Write-Log "Error during ingestion: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-FileWatcher {
    param([string]$WatchDir, [int]$DebounceMs = 2000)

    Write-Log "Setting up file watcher for: $WatchDir"

    if (-not (Test-Path $WatchDir)) {
        Write-Log "Watch directory does not exist: $WatchDir" "ERROR"
        return
    }

    # Create file system watcher
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $WatchDir
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $false

    # File filters
    $watcher.Filter = "*.*"

    # Debounce timer
    $debounceTimer = $null
    $pendingChanges = @{}

    $action = {
        param($sender, $event)

        $filePath = $event.FullPath
        $changeType = $event.ChangeType
        $fileName = [System.IO.Path]::GetFileName($filePath)
        $fileExt = [System.IO.Path]::GetExtension($filePath).ToLower()

        # Check if file type is supported
        $supportedExts = @(".md", ".pdf", ".json")
        if ($fileExt -notin $supportedExts) {
            if ($Verbose) {
                Write-Log "Skipping unsupported file type: $filePath" "DEBUG"
            }
            return
        }

        # Skip temporary and hidden files
        if ($fileName.StartsWith(".") -or $fileName.EndsWith(".tmp") -or $fileName.EndsWith(".bak")) {
            if ($Verbose) {
                Write-Log "Skipping temporary/hidden file: $filePath" "DEBUG"
            }
            return
        }

        Write-Log "Detected change: $changeType - $filePath"

        # Add to pending changes
        $pendingChanges[$filePath] = @{
            ChangeType = $changeType
            Timestamp = Get-Date
        }

        # Reset debounce timer
        if ($debounceTimer) {
            $debounceTimer.Stop()
            $debounceTimer.Dispose()
        }

        $debounceTimer = New-Object System.Timers.Timer
        $debounceTimer.Interval = $DebounceMs
        $debounceTimer.AutoReset = $false

        $debounceTimer.add_Elapsed({
            Write-Log "Debounce period ended, processing $($pendingChanges.Count) changes"

            # Get unique directories to re-ingest
            $dirsToProcess = @{}
            foreach ($change in $pendingChanges.Values) {
                $dir = [System.IO.Path]::GetDirectoryName($change.FilePath)
                $dirsToProcess[$dir] = $true
            }

            $pendingChanges.Clear()

            # Process each directory
            foreach ($dir in $dirsToProcess.Keys) {
                Write-Log "Re-ingesting directory: $dir"
                $success = Invoke-RAGIngestion -Paths $dir

                if ($success) {
                    Write-Log "Successfully re-ingested: $dir"
                } else {
                    Write-Log "Failed to re-ingest: $dir" "ERROR"
                }
            }
        })

        $debounceTimer.Start()
    }

    # Register event handlers
    $watcherEvent = Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action
    $watcherCreate = Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
    $watcherDelete = Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action $action

    Write-Log "File watcher started. Monitoring for changes..."
    Write-Log "Supported file types: .md, .pdf, .json"
    Write-Log "Debounce delay: $($DebounceMs/1000) seconds"
    Write-Log "Press Ctrl+C to stop"

    # Enable the watcher
    $watcher.EnableRaisingEvents = $true

    # Keep the script running
    try {
        while ($true) {
            Start-Sleep -Seconds 1

            # Periodic status
            if ($Verbose -and (Get-Date).Second % 30 -eq 0) {
                Write-Log "Watcher active - monitoring $WatchDir" "DEBUG"
            }
        }
    } finally {
        # Cleanup
        Write-Log "Stopping file watcher..."

        if ($debounceTimer) {
            $debounceTimer.Stop()
            $debounceTimer.Dispose()
        }

        $watcher.EnableRaisingEvents = $false
        $watcher.Dispose()

        Unregister-Event -SourceIdentifier $watcherEvent.Name -ErrorAction SilentlyContinue
        Unregister-Event -SourceIdentifier $watcherCreate.Name -ErrorAction SilentlyContinue
        Unregister-Event -SourceIdentifier $watcherDelete.Name -ErrorAction SilentlyContinue

        Write-Log "File watcher stopped"
    }
}

# Main execution
Write-Log "=== RAG Auto-Ingestion Watcher Starting ==="
Write-Log "Watch Directory: $WatchDirectory"
Write-Log "Config File: $ConfigPath"
Write-Log "Debounce Seconds: $DebounceSeconds"
Write-Log "One-shot Mode: $OneShot"

# Validate environment
if (-not (Test-PythonEnvironment)) {
    exit 1
}

if (-not (Test-VirtualEnvironment)) {
    Write-Log "Continuing without virtual environment validation..." "WARN"
}

# Run initial ingestion if in one-shot mode or always
if ($OneShot) {
    Write-Log "Running one-shot ingestion..."
    $success = Invoke-RAGIngestion -Paths $WatchDirectory

    if ($success) {
        Write-Log "One-shot ingestion completed successfully"
        exit 0
    } else {
        Write-Log "One-shot ingestion failed" "ERROR"
        exit 1
    }
} else {
    # Run initial ingestion
    Write-Log "Running initial ingestion..."
    Invoke-RAGIngestion -Paths $WatchDirectory

    # Start file watcher
    Write-Log "Starting continuous file watching..."
    Start-FileWatcher -WatchDir $WatchDirectory -DebounceMs ($DebounceSeconds * 1000)
}
