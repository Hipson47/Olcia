@echo off
REM E2E Test Batch Script for MCP+RAG System
REM Windows batch script to run end-to-end testing locally

echo 🚀 Starting MCP+RAG E2E Test...

REM Change to script directory then project root
cd /d "%~dp0.."

REM Step 1: Ensure knowledge directory exists
echo 📁 Checking knowledge directory...
if not exist "knowledge" (
    mkdir knowledge
    echo   Created knowledge directory
)

REM Step 2: Create or verify e2e test document exists
echo 📄 Ensuring E2E test document exists...
if not exist "knowledge\e2e.md" (
    echo # MCP+RAG E2E Test Document > "knowledge\e2e.md"
    echo. >> "knowledge\e2e.md"
    echo This is a test document for end-to-end testing of the MCP+RAG system. >> "knowledge\e2e.md"
    echo. >> "knowledge\e2e.md"
    echo ## Features >> "knowledge\e2e.md"
    echo. >> "knowledge\e2e.md"
    echo - Vector search using ChromaDB >> "knowledge\e2e.md"
    echo - JSON-RPC communication >> "knowledge\e2e.md"
    echo - Document ingestion pipeline >> "knowledge\e2e.md"
    echo - Semantic search capabilities >> "knowledge\e2e.md"
    echo. >> "knowledge\e2e.md"
    echo ## Architecture >> "knowledge\e2e.md"
    echo. >> "knowledge\e2e.md"
    echo The system consists of: >> "knowledge\e2e.md"
    echo 1. MCP server for protocol handling >> "knowledge\e2e.md"
    echo 2. ChromaDB for vector storage >> "knowledge\e2e.md"
    echo 3. Sentence transformers for embeddings >> "knowledge\e2e.md"
    echo 4. RAG ingestion pipeline >> "knowledge\e2e.md"
    echo   Created E2E test document: knowledge\e2e.md
) else (
    echo   E2E test document already exists: knowledge\e2e.md
)

REM Step 3: Run document ingestion
echo 🔄 Running document ingestion...
python rag/ingest.py --paths knowledge/
if %ERRORLEVEL% neq 0 (
    echo ❌ Ingestion failed with exit code %ERRORLEVEL%
    exit /b 1
)
echo   ✅ Ingestion completed successfully

REM Step 4: Test JSON-RPC communication
echo 🔍 Testing JSON-RPC search query...

REM Create a temporary file with the JSON-RPC request
echo {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"rag.search","arguments":{"query":"MCP system architecture","k":3}}} > temp_request.json

REM Run the MCP server with the JSON-RPC request
type temp_request.json | python mcp/server.py > temp_response.txt
set SERVER_EXIT=%ERRORLEVEL%

REM Clean up temp files
del temp_request.json

if %SERVER_EXIT% neq 0 (
    echo ❌ Server failed with exit code %SERVER_EXIT%
    type temp_response.txt
    del temp_response.txt
    exit /b 1
)

REM Parse and validate JSON response
echo 📋 Server response:
type temp_response.txt

REM Simple validation - check if response contains expected JSON structure
REM Read the response and check for key elements
set RESPONSE_VALID=0
type temp_response.txt | findstr "jsonrpc.*2.0" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    type temp_response.txt | findstr "result" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        type temp_response.txt | findstr "chunks" >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set RESPONSE_VALID=1
        )
    )
)

if %RESPONSE_VALID% equ 0 (
    echo ❌ Invalid JSON-RPC response format
    del temp_response.txt
    exit /b 1
)

echo   ✅ JSON-RPC response validated

REM Clean up
del temp_response.txt

REM Step 5: Success summary
echo.
echo 🎉 E2E Test Completed Successfully!
echo    ✅ Knowledge ingestion: PASSED
echo    ✅ JSON-RPC communication: PASSED
echo    ✅ Response validation: PASSED

echo.
echo Press any key to exit...
pause >nul
