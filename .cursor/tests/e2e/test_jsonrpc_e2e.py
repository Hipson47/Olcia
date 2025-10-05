#!/usr/bin/env python3
"""
End-to-end tests for MCP server JSON-RPC functionality.
Tests full ingestion -> server -> search pipeline.
"""

import asyncio
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Optional

import pytest

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.ingest import RAGIngestor


@pytest.mark.e2e
class TestJSONRPCEndToEnd(unittest.TestCase):
    """End-to-end tests for MCP server JSON-RPC communication."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for hermetic testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.knowledge_dir = self.temp_dir / "knowledge"
        self.rag_store_dir = self.temp_dir / "rag" / "store"
        self.memory_dir = self.temp_dir / "memory"

        # Create directories
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.rag_store_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Store original environment
        self.original_cwd = os.getcwd()

        # Change to temp directory for hermetic operation
        os.chdir(self.temp_dir)

        # Server process
        self.server_process: subprocess.Popen | None = None

    def tearDown(self):
        """Clean up test fixtures."""
        # Kill server process if still running
        if self.server_process and self.server_process.poll() is None:
            try:
                if os.name == 'nt':  # Windows
                    self.server_process.terminate()
                    time.sleep(0.1)  # Give it time to terminate gracefully
                    if self.server_process.poll() is None:
                        self.server_process.kill()
                else:  # Unix-like
                    self.server_process.terminate()
                    try:
                        self.server_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.server_process.kill()
                        self.server_process.wait()
            except Exception:
                pass  # Best effort cleanup

        # Restore original working directory
        os.chdir(self.original_cwd)

        # Clean up temp directory
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass  # Best effort cleanup

    def create_sample_knowledge_file(self) -> Path:
        """Create a sample knowledge file for testing."""
        content = """# MCP+RAG System Architecture

The MCP+RAG system is a Model Context Protocol server with Retrieval-Augmented Generation capabilities.

## Core Components

### ChromaDB Vector Database
- Stores document embeddings for semantic search
- Persistent storage in SQLite format
- Optimized for high-dimensional vector operations

### Sentence Transformers
- Generates embeddings using pre-trained models
- All-MiniLM-L6-v2 model for efficient processing
- CPU-optimized for local execution

### MCP Protocol Layer
- JSON-RPC 2.0 based communication
- Stdio transport for Cursor integration
- Tool-based API for various operations

## Key Features

- **Semantic Search**: Find relevant content using natural language queries
- **Document Ingestion**: Process PDFs, Markdown, and text files
- **Memory Management**: Track conversation context and lessons learned
- **Agent Orchestration**: Route tasks to specialized agents based on goals
"""

        knowledge_file = self.knowledge_dir / "e2e_sample.md"
        knowledge_file.write_text(content, encoding='utf-8')
        return knowledge_file

    def run_ingestion(self) -> bool:
        """Run document ingestion using RAGIngestor."""
        try:
            ingestor = RAGIngestor(persist_directory=str(self.rag_store_dir))
            result = ingestor.ingest_directory(self.knowledge_dir)

            # Check if ingestion was successful
            if result and any(r.get("status") == "success" for r in result):
                return True

            print(f"Ingestion result: {result}")
            return False

        except Exception as e:
            print(f"Ingestion failed: {e}")
            return False

    def start_server(self) -> bool:
        """Start the MCP server process."""
        try:
            # Set environment variables for the server
            env = os.environ.copy()
            # Add project root to path (where mcp module is located)
            project_root = Path(__file__).parent.parent.parent
            env['PYTHONPATH'] = str(project_root)

            # Start server with custom store path
            cmd = [
                sys.executable,
                "-m", "mcp.server"
            ]

            self.server_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                env=env,
                cwd=str(self.temp_dir)
            )

            # Give server time to start up
            time.sleep(2)

            # Check if process is still running
            if self.server_process.poll() is None:
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                print(f"Server failed to start. STDOUT: {stdout}, STDERR: {stderr}")
                return False

        except Exception as e:
            print(f"Failed to start server: {e}")
            return False

    def send_jsonrpc_request(self, request: dict) -> dict:
        """Send a JSON-RPC request to the server and get response."""
        if not self.server_process or self.server_process.poll() is not None:
            raise RuntimeError("Server process not running")

        try:
            # Send request
            request_line = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_line)
            self.server_process.stdin.flush()

            # Read response line
            response_line = self.server_process.stdout.readline().strip()

            if not response_line:
                raise RuntimeError("No response received from server")

            # Parse JSON response
            response = json.loads(response_line)

            return response

        except Exception as e:
            # Get any error output
            try:
                if self.server_process.stderr:
                    error_output = self.server_process.stderr.read()
                    print(f"Server stderr: {error_output}")
            except Exception:
                pass

            raise RuntimeError(f"Failed to communicate with server: {e}")

    def test_full_ingestion_to_search_pipeline(self):
        """Test the complete pipeline: ingest docs -> start server -> search."""

        # Step 1: Create sample knowledge file
        knowledge_file = self.create_sample_knowledge_file()
        self.assertTrue(knowledge_file.exists(), "Sample knowledge file should be created")

        # Step 2: Run ingestion
        ingestion_success = self.run_ingestion()
        self.assertTrue(ingestion_success, "Document ingestion should succeed")

        # Verify ChromaDB files were created
        chroma_files = list(self.rag_store_dir.glob("*.sqlite3"))
        self.assertTrue(len(chroma_files) > 0, "ChromaDB database files should be created")

        # Step 3: Start MCP server
        server_started = self.start_server()
        self.assertTrue(server_started, "MCP server should start successfully")

        # Step 4: Test tools/list to verify server is responsive
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }

        try:
            list_response = self.send_jsonrpc_request(list_request)

            # Validate response structure
            self.assertEqual(list_response["jsonrpc"], "2.0")
            self.assertEqual(list_response["id"], 1)
            self.assertIn("result", list_response)
            self.assertIn("tools", list_response["result"])

            # Verify rag.search tool is available
            tool_names = [tool["name"] for tool in list_response["result"]["tools"]]
            self.assertIn("rag.search", tool_names, "rag.search tool should be available")

        except Exception as e:
            self.fail(f"tools/list request failed: {e}")

        # Step 5: Test rag.search with a query that should find our sample content
        search_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "rag.search",
                "arguments": {
                    "query": "MCP+RAG system architecture",
                    "k": 3
                }
            }
        }

        try:
            search_response = self.send_jsonrpc_request(search_request)

            # Validate response structure
            self.assertEqual(search_response["jsonrpc"], "2.0")
            self.assertEqual(search_response["id"], 2)
            self.assertIn("result", search_response, "Response should contain result")

            result = search_response["result"]
            self.assertIn("chunks", result, "Result should contain chunks")

            chunks = result["chunks"]
            self.assertIsInstance(chunks, list, "Chunks should be a list")

            # Should find at least one relevant chunk from our sample document
            self.assertGreater(len(chunks), 0, "Should find at least one chunk")

            # Validate chunk structure
            chunk = chunks[0]
            self.assertIn("text", chunk, "Chunk should have text")
            self.assertIn("path", chunk, "Chunk should have path")
            self.assertIn("idx", chunk, "Chunk should have idx")
            self.assertIn("score", chunk, "Chunk should have score")

            # Verify the chunk contains relevant content
            chunk_text = chunk["text"].lower()
            self.assertTrue(
                any(keyword in chunk_text for keyword in ["mcp", "rag", "architecture", "chromadb", "vector"]),
                f"Chunk text should contain relevant keywords: {chunk_text[:200]}..."
            )

        except Exception as e:
            self.fail(f"rag.search request failed: {e}")

    def test_server_handles_invalid_requests(self):
        """Test server handles invalid JSON-RPC requests gracefully."""

        # Start server
        knowledge_file = self.create_sample_knowledge_file()
        ingestion_success = self.run_ingestion()
        self.assertTrue(ingestion_success)

        server_started = self.start_server()
        self.assertTrue(server_started)

        # Test invalid method
        invalid_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "nonexistent.method"
        }

        try:
            response = self.send_jsonrpc_request(invalid_request)

            # Should get a method not found error
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 3)
            self.assertIn("error", response)
            self.assertEqual(response["error"]["code"], -32601)

        except Exception as e:
            self.fail(f"Invalid method test failed: {e}")

    def test_server_handles_malformed_json(self):
        """Test server handles malformed JSON gracefully."""

        # Start server
        knowledge_file = self.create_sample_knowledge_file()
        ingestion_success = self.run_ingestion()
        self.assertTrue(ingestion_success)

        server_started = self.start_server()
        self.assertTrue(server_started)

        # Send malformed JSON
        try:
            malformed_request = '{"jsonrpc": "2.0", "id": 4, invalid json}'
            self.server_process.stdin.write(malformed_request + "\n")
            self.server_process.stdin.flush()

            # Read response
            response_line = self.server_process.stdout.readline().strip()
            response = json.loads(response_line)

            # Should get a parse error
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("error", response)
            self.assertEqual(response["error"]["code"], -32700)

        except Exception as e:
            self.fail(f"Malformed JSON test failed: {e}")


if __name__ == '__main__':
    unittest.main()
