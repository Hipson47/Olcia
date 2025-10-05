# E2E Test Script for MCP+RAG System
# Windows PowerShell script to run end-to-end testing locally

# Set strict error handling
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:ErrorAction'] = 'Stop'

Write-Host "🚀 Starting MCP+RAG E2E Test..." -ForegroundColor Green

# Get script directory and project root
$ScriptDir = Split-Path -Parent $PSCommandPath
$ProjectRoot = Split-Path -Parent $ScriptDir

# Change to project root directory
Push-Location $ProjectRoot

try {
    # Step 1: Ensure knowledge directory exists
    Write-Host "📁 Checking knowledge directory..." -ForegroundColor Blue
    $KnowledgeDir = Join-Path $ProjectRoot "knowledge"
    if (-not (Test-Path $KnowledgeDir)) {
        New-Item -ItemType Directory -Path $KnowledgeDir | Out-Null
        Write-Host "  Created knowledge directory" -ForegroundColor Gray
    }

    # Step 2: Create or verify e2e test document exists
    Write-Host "📄 Ensuring E2E test document exists..." -ForegroundColor Blue
    $E2eFile = Join-Path $KnowledgeDir "e2e.md"
    if (-not (Test-Path $E2eFile)) {
        $TestContent = @"
# MCP+RAG E2E Test Document

This document is used for end-to-end testing of the MCP+RAG system.

## Test Content

The system should be able to:
- Ingest this document into the knowledge base
- Generate embeddings for semantic search
- Respond to JSON-RPC queries
- Return relevant chunks based on similarity

## Architecture Overview

- **MCP Server**: Handles JSON-RPC protocol communication
- **ChromaDB**: Vector database for knowledge storage
- **Sentence Transformers**: Embedding generation
- **RAG Pipeline**: Retrieval-augmented generation

## Test Query

Try searching for: "MCP system architecture"
"@
        $TestContent | Out-File -FilePath $E2eFile -Encoding UTF8
        Write-Host "  Created E2E test document: $E2eFile" -ForegroundColor Gray
    } else {
        Write-Host "  E2E test document already exists: $E2eFile" -ForegroundColor Gray
    }

    # Step 3: Run document ingestion
    Write-Host "🔄 Running document ingestion..." -ForegroundColor Blue
    $IngestCommand = "python rag/ingest.py --paths knowledge/"
    Write-Host "  Executing: $IngestCommand" -ForegroundColor Gray

    # Run ingestion and capture output
    $IngestOutput = Invoke-Expression $IngestCommand 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Ingestion failed with exit code $LASTEXITCODE"
        Write-Host "Ingestion output:" -ForegroundColor Red
        $IngestOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        exit 1
    }

    Write-Host "  ✅ Ingestion completed successfully" -ForegroundColor Green
    Write-Host "  Ingestion summary:" -ForegroundColor Gray
    $IngestOutput | Where-Object { $_ -match "Successfully ingested" } | ForEach-Object {
        Write-Host "    $_" -ForegroundColor Gray
    }

    # Step 4: Test JSON-RPC communication
    Write-Host "🔍 Testing JSON-RPC search query..." -ForegroundColor Blue

    # Create JSON-RPC request
    $JsonRpcRequest = @{
        jsonrpc = "2.0"
        id = 1
        method = "tools/call"
        params = @{
            name = "rag.search"
            arguments = @{
                query = "MCP system architecture"
                k = 3
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress

    Write-Host "  Sending JSON-RPC request:" -ForegroundColor Gray
    Write-Host "    $JsonRpcRequest" -ForegroundColor Gray

    # Run the MCP server with the JSON-RPC request
    $ServerCommand = "echo '$JsonRpcRequest' | python mcp/server.py"
    Write-Host "  Executing: $ServerCommand" -ForegroundColor Gray

    # Run server and capture output
    $ServerOutput = Invoke-Expression $ServerCommand 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Server failed with exit code $LASTEXITCODE"
        Write-Host "Server output:" -ForegroundColor Red
        $ServerOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        exit 1
    }

    # Parse and validate JSON response
    Write-Host "  📋 Server response:" -ForegroundColor Gray
    $ResponseLine = $ServerOutput | Where-Object { $_ -match "^{\s*\{.*\}" } | Select-Object -First 1

    if (-not $ResponseLine) {
        Write-Error "No JSON response found in server output"
        Write-Host "Full server output:" -ForegroundColor Red
        $ServerOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        exit 1
    }

    Write-Host "    $ResponseLine" -ForegroundColor Gray

    # Validate JSON structure
    try {
        $Response = $ResponseLine | ConvertFrom-Json

        # Check required fields
        if (-not $Response.jsonrpc -or $Response.jsonrpc -ne "2.0") {
            throw "Invalid JSON-RPC version"
        }
        if (-not $Response.id -or $Response.id -ne 1) {
            throw "Invalid response ID"
        }
        if (-not $Response.result) {
            throw "No result field in response"
        }
        if (-not $Response.result.chunks) {
            throw "No chunks in result"
        }

        $ChunkCount = $Response.result.chunks.Count
        Write-Host "  ✅ JSON-RPC response validated" -ForegroundColor Green
        Write-Host "  📊 Found $ChunkCount relevant chunks" -ForegroundColor Green

        # Show sample chunk content
        if ($ChunkCount -gt 0) {
            Write-Host "  📖 Sample chunk preview:" -ForegroundColor Gray
            $FirstChunk = $Response.result.chunks[0]
            $Preview = $FirstChunk.text.Substring(0, [Math]::Min(100, $FirstChunk.text.Length))
            Write-Host "    '$Preview...'" -ForegroundColor Gray
        }

    } catch {
        Write-Error "Failed to validate JSON response: $_"
        Write-Host "Raw response: $ResponseLine" -ForegroundColor Red
        exit 1
    }

    # Step 5: Success summary
    Write-Host "" -ForegroundColor White
    Write-Host "🎉 E2E Test Completed Successfully!" -ForegroundColor Green
    Write-Host "   ✅ Knowledge ingestion: PASSED" -ForegroundColor Green
    Write-Host "   ✅ JSON-RPC communication: PASSED" -ForegroundColor Green
    Write-Host "   ✅ Response validation: PASSED" -ForegroundColor Green

} catch {
    Write-Host "" -ForegroundColor White
    Write-Host "❌ E2E Test Failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # Restore original location
    Pop-Location
}
