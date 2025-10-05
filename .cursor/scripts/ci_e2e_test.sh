#!/bin/bash
set -e

# CI E2E Test Script
# This script runs the complete E2E test pipeline in a container

echo "Running E2E test..."

# Create sample knowledge file
mkdir -p /app/knowledge
cat > /app/knowledge/e2e_sample.md << 'EOF'
# E2E Test Document

This is a test document for end-to-end testing of the MCP+RAG system.

## Features

- Vector search using ChromaDB
- JSON-RPC communication
- Document ingestion pipeline
- Semantic search capabilities

## Architecture

The system consists of:
1. MCP server for protocol handling
2. ChromaDB for vector storage
3. Sentence transformers for embeddings
4. RAG ingestion pipeline
EOF

echo 'Sample document created'

# Ingest the document
echo 'Starting ingestion...'
echo 'Testing imports first...'
python -c "
import sys
print('Python path:', sys.path[:3])
try:
    from ruamel.yaml import YAML
    print('✓ ruamel.yaml module available')
except ImportError as e:
    print('✗ ruamel.yaml module missing:', e)
    exit(1)

try:
    import chromadb
    print('✓ chromadb available')
except ImportError as e:
    print('✗ chromadb missing:', e)
    exit(1)
"
echo 'Running ingestion...'
python -c "
import sys
from pathlib import Path
sys.path.insert(0, '.')
from rag.ingest import RAGIngestor
ingestor = RAGIngestor(persist_directory='store')
result = ingestor.ingest_directory(Path('knowledge'))
print(f'Ingestion result: {result}')
success = any(r.get('status') == 'success' for r in result)
print(f'Ingestion successful: {success}')
exit(0 if success else 1)
"

if [ $? -ne 0 ]; then
  echo 'Ingestion failed'
  exit 1
fi

echo 'Ingestion completed successfully'

# Test JSON-RPC search
echo 'Testing JSON-RPC search...'
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"rag.search","arguments":{"query":"MCP system architecture","k":2}}}' | \
timeout 30 python mcp/server.py

echo "E2E test completed successfully"
