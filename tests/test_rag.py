#!/usr/bin/env python3
"""
Unit tests for RAG ingestion system.
Tests chunking, file loading, and ingest logic with mocked embeddings.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add rag directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.ingest import TextChunker, FileLoader, RAGIngestor
from mcp.server import MCPServer


class TestTextChunker(unittest.TestCase):
    """Test text chunking functionality."""

    def setUp(self):
        self.chunker = TextChunker(chunk_size=10, overlap_percent=0.2)

    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        text = "This is a test document with multiple sentences. It should be chunked properly."
        chunks = self.chunker.chunk_text(text)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        # Check that chunks are strings
        for chunk in chunks:
            self.assertIsInstance(chunk, str)
            self.assertGreater(len(chunk), 0)

    def test_chunk_text_with_overlap(self):
        """Test that chunks have proper overlap."""
        # Create longer text that will definitely exceed chunk size
        text = "This is a very long sentence that contains many words and should definitely exceed the chunk size limit. " * 20
        chunks = self.chunker.chunk_text(text)

        # With the long text, we should have multiple chunks
        self.assertGreater(len(chunks), 1)

        # Check that consecutive chunks share some content
        if len(chunks) > 1:
            first_words = set(chunks[0].split())
            second_words = set(chunks[1].split())
            overlap = first_words.intersection(second_words)
            self.assertGreater(len(overlap), 0, "Chunks should have overlap")

    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        chunks = self.chunker.chunk_text("")
        self.assertEqual(chunks, [])

    def test_chunk_text_short(self):
        """Test chunking text shorter than chunk size."""
        text = "short text"
        chunks = self.chunker.chunk_text(text)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)


class TestFileLoader(unittest.TestCase):
    """Test file loading functionality."""

    def setUp(self):
        self.loader = FileLoader()

    def test_load_markdown_file(self):
        """Test loading markdown files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = "# Test Header\n\nThis is test content."
            f.write(content)
            temp_path = f.name

        try:
            loaded_content = self.loader.load_file(temp_path)
            self.assertEqual(loaded_content, content)
        finally:
            os.unlink(temp_path)

    def test_load_json_file(self):
        """Test loading JSON files."""
        test_data = {"key": "value", "number": 42}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            loaded_content = self.loader.load_file(temp_path)
            self.assertIn("key", loaded_content)
            self.assertIn("value", loaded_content)
        finally:
            os.unlink(temp_path)

    @patch('fitz.open')
    def test_load_pdf_file(self, mock_fitz_open):
        """Test loading PDF files with mocked PyMuPDF."""
        # Mock PDF document
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF content from page 1"
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.__enter__ = Mock(return_value=mock_doc)
        mock_doc.__exit__ = Mock(return_value=None)
        mock_fitz_open.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            loaded_content = self.loader.load_file(temp_path)
            self.assertEqual(loaded_content, "PDF content from page 1")
            mock_fitz_open.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_unsupported_file(self):
        """Test loading unsupported file type."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            with self.assertRaises(ValueError):
                self.loader.load_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_file("nonexistent_file.md")


class TestRAGIngestor(unittest.TestCase):
    """Test RAG ingestion functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ingestor = RAGIngestor(persist_directory=self.temp_dir)

    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('chromadb.PersistentClient')
    @patch('rag.ingest.SentenceTransformer')
    def test_ingest_file_success(self, mock_sentence_transformer, mock_persistent_client):
        """Test successful file ingestion."""
        # Mock embedding model
        mock_model = Mock()
        mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]  # Make it directly iterable
        mock_model.encode.return_value = mock_embeddings
        mock_sentence_transformer.return_value = mock_model

        # Mock ChromaDB
        mock_collection = Mock()
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Create ingestor with mocks
        ingestor = RAGIngestor(persist_directory=self.temp_dir)

        # Create test file
        test_file = Path(self.temp_dir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is test content.")

        # Ingest file
        result = ingestor.ingest_file(test_file)

        # Verify results
        self.assertIsInstance(result, dict)
        self.assertIn("file_path", result)
        self.assertIn("chunks_count", result)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

        # Verify ChromaDB calls
        mock_collection.add.assert_called()

    @patch('chromadb.PersistentClient')
    @patch('rag.ingest.SentenceTransformer')
    def test_ingest_directory(self, mock_sentence_transformer, mock_persistent_client):
        """Test directory ingestion."""
        # Mock embedding model
        mock_model = Mock()
        mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]  # Make it directly iterable
        mock_model.encode.return_value = mock_embeddings
        mock_sentence_transformer.return_value = mock_model

        # Mock ChromaDB
        mock_collection = Mock()
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Create test files
        test_dir = Path(self.temp_dir) / "test_docs"
        test_dir.mkdir()

        (test_dir / "doc1.md").write_text("# Doc 1\n\nContent 1")
        (test_dir / "doc2.json").write_text('{"key": "value"}')

        # Ingest directory
        results = self.ingestor.ingest_directory(test_dir)

        # Verify results
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        for result in results:
            self.assertIn("status", result)
            self.assertEqual(result["status"], "success")

    def test_ingest_file_not_found(self):
        """Test ingestion of non-existent file."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.md"

        result = self.ingestor.ingest_file(nonexistent_file)

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)

    def test_windows_path_handling(self):
        """Test Windows path handling."""
        # Test with backslashes (Windows style)
        test_path = "C:\\Users\\test\\document.md"
        normalized = self.ingestor._normalize_path(test_path)

        # Should work on both Windows and Unix
        self.assertIsInstance(normalized, Path)

    def test_embedding_error_handling(self):
        """Test handling of embedding errors."""
        # Create ingestor with mocked embedding model
        with patch('rag.ingest.SentenceTransformer') as mock_sentence_transformer:
            # Mock embedding model to raise exception
            mock_model = Mock()
            mock_model.encode.side_effect = Exception("Embedding failed")
            mock_sentence_transformer.return_value = mock_model

            # Create ingestor with mocked model
            ingestor = RAGIngestor(persist_directory=self.temp_dir)

            # Create test file
            test_file = Path(self.temp_dir) / "test.md"
            test_file.write_text("# Test\n\nContent")

            result = ingestor.ingest_file(test_file)

            self.assertEqual(result["status"], "error")
            self.assertIn("Embedding failed", result["error"])


class TestMCPServer(unittest.TestCase):
    """Test MCP server functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Create a mock server for testing
        self.server = MCPServer()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('mcp.server.RAGIngestor')
    def test_ingest_files_success(self, mock_ingestor_class):
        """Test successful file ingestion through MCP server."""
        # Mock the ingestor
        mock_ingestor = Mock()
        mock_ingestor.ingest_file.return_value = {"status": "success", "chunks_count": 2}
        mock_ingestor_class.return_value = mock_ingestor

        # Create test file
        test_file = Path(self.temp_dir) / "test.md"
        test_file.write_text("# Test\n\nContent")

        # Test ingestion
        result = self.server.ingest_files([str(test_file)])

        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 2)
        mock_ingestor.ingest_file.assert_called_once()

    def test_ingest_files_not_found(self):
        """Test ingestion of non-existent files."""
        result = self.server.ingest_files(["nonexistent.md"])

        self.assertFalse(result["ok"])
        self.assertEqual(result["count"], 0)

    @patch('mcp.server.chromadb.PersistentClient')
    @patch('mcp.server.SentenceTransformer')
    def test_rag_search_tool(self, mock_sentence_transformer, mock_persistent_client):
        """Test rag.search tool functionality."""
        # Mock ChromaDB
        mock_collection = Mock()
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Mock search results
        mock_collection.query.return_value = {
            'ids': [['chunk1', 'chunk2']],
            'documents': [['Document text 1', 'Document text 2']],
            'metadatas': [[
                {'source_file': 'test.md', 'chunk_index': 0},
                {'source_file': 'test.md', 'chunk_index': 1}
            ]],
            'distances': [[0.1, 0.2]]
        }

        # Mock embeddings
        mock_model = Mock()
        mock_embedding_result = Mock()
        mock_embedding_result.tolist.return_value = [0.1, 0.2, 0.3]
        mock_model.encode.return_value = mock_embedding_result
        mock_sentence_transformer.return_value = mock_model

        # Create server and test search
        server = MCPServer()
        result = server.rag_server.search_knowledge_chunks("test query", 2)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("text", result[0])
        self.assertIn("path", result[0])
        self.assertIn("idx", result[0])
        self.assertIn("score", result[0])

    def test_mcp_message_handling_initialize(self):
        """Test MCP initialize message handling."""
        import asyncio
        async def test():
            message = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
            response = await self.server.handle_message(message)

            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 1)
            self.assertIn("result", response)
            self.assertIn("serverInfo", response["result"])

        asyncio.run(test())

    def test_mcp_message_handling_tools_list(self):
        """Test MCP tools/list message handling."""
        import asyncio
        async def test():
            message = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            response = await self.server.handle_message(message)

            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 2)
            self.assertIn("result", response)
            self.assertIn("tools", response["result"])

            # Check that our new tools are present
            tool_names = [tool["name"] for tool in response["result"]["tools"]]
            self.assertIn("rag.search", tool_names)
            self.assertIn("rag.ingest", tool_names)

        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
