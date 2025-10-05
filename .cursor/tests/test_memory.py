#!/usr/bin/env python3
"""
Unit tests for memory logging system.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add current directory to path for imports
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.memory import MemoryLogger, MemoryEntry, log_memory


class TestMemoryEntry(unittest.TestCase):
    """Test MemoryEntry dataclass functionality."""

    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        entry = MemoryEntry(
            timestamp=1234567890.0,
            event="Test event",
            detail="Test detail",
            hint="Test hint"
        )

        self.assertEqual(entry.timestamp, 1234567890.0)
        self.assertEqual(entry.event, "Test event")
        self.assertEqual(entry.detail, "Test detail")
        self.assertEqual(entry.hint, "Test hint")

    def test_memory_entry_to_dict(self):
        """Test converting memory entry to dictionary."""
        entry = MemoryEntry(
            timestamp=1234567890.0,
            event="Test event",
            detail="Test detail"
        )

        entry_dict = entry.to_dict()
        expected = {
            "timestamp": 1234567890.0,
            "event": "Test event",
            "detail": "Test detail",
            "hint": None
        }

        self.assertEqual(entry_dict, expected)


class TestMemoryLogger(unittest.TestCase):
    """Test MemoryLogger functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mistakes_file = Path(self.temp_dir) / "mistakes.jsonl"
        self.logger = MemoryLogger(self.mistakes_file)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_error_basic(self):
        """Test basic error logging."""
        success = self.logger.log_error("Test event", "Test detail")

        self.assertTrue(success)
        self.assertTrue(self.mistakes_file.exists())

        # Verify the file contains one JSON line
        with open(self.mistakes_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)

            entry = json.loads(lines[0])
            self.assertEqual(entry["event"], "Test event")
            self.assertEqual(entry["detail"], "Test detail")
            self.assertIsNone(entry["hint"])
            self.assertIsInstance(entry["timestamp"], float)

    def test_log_error_with_hint(self):
        """Test error logging with hint."""
        success = self.logger.log_error("Test event", "Test detail", "Test hint")

        self.assertTrue(success)

        with open(self.mistakes_file, 'r') as f:
            entry = json.loads(f.read())
            self.assertEqual(entry["hint"], "Test hint")

    def test_log_error_multiple_entries(self):
        """Test logging multiple entries."""
        self.logger.log_error("Event 1", "Detail 1")
        self.logger.log_error("Event 2", "Detail 2", "Hint 2")

        with open(self.mistakes_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)

            entry1 = json.loads(lines[0])
            entry2 = json.loads(lines[1])

            self.assertEqual(entry1["event"], "Event 1")
            self.assertEqual(entry2["event"], "Event 2")
            self.assertEqual(entry2["hint"], "Hint 2")

    def test_get_recent_entries_empty(self):
        """Test getting recent entries from empty file."""
        entries = self.logger.get_recent_entries()
        self.assertEqual(entries, [])

    def test_get_recent_entries(self):
        """Test getting recent entries."""
        # Log some entries
        self.logger.log_error("Event 1", "Detail 1")
        self.logger.log_error("Event 2", "Detail 2")
        self.logger.log_error("Event 3", "Detail 3")

        entries = self.logger.get_recent_entries(limit=2)

        # Should return 2 most recent entries
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["event"], "Event 3")  # Most recent first
        self.assertEqual(entries[1]["event"], "Event 2")

    def test_get_recent_entries_limit(self):
        """Test limiting the number of recent entries."""
        # Log 5 entries
        for i in range(5):
            self.logger.log_error(f"Event {i}", f"Detail {i}")

        entries = self.logger.get_recent_entries(limit=3)
        self.assertEqual(len(entries), 3)

    def test_log_memory_function(self):
        """Test the log_memory function interface."""
        result = log_memory("Test event", "Test detail", "Test hint")

        self.assertEqual(result, {"ok": True})

    def test_file_creation(self):
        """Test that the logger creates the file if it doesn't exist."""
        # Remove the file
        if self.mistakes_file.exists():
            self.mistakes_file.unlink()

        # Create new logger - should create file
        logger2 = MemoryLogger(self.mistakes_file)
        self.assertTrue(self.mistakes_file.exists())

    def test_directory_creation(self):
        """Test that the logger creates the directory if it doesn't exist."""
        nested_file = Path(self.temp_dir) / "subdir" / "nested" / "mistakes.jsonl"

        logger = MemoryLogger(nested_file)
        self.assertTrue(nested_file.exists())
        self.assertTrue(nested_file.parent.exists())


class TestMemoryIntegration(unittest.TestCase):
    """Test memory system integration."""

    def test_mcp_server_memory_tool(self):
        """Test that memory.log tool is registered in MCP server."""
        import asyncio
        from mcp.server import MCPServer

        server = MCPServer()

        async def test():
            # Test tools/list includes memory.log
            message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }

            response = await server.handle_message(message)
            tool_names = [tool["name"] for tool in response["result"]["tools"]]

            self.assertIn("memory.log", tool_names)

        asyncio.run(test())

    def test_memory_log_tool_call(self):
        """Test calling memory.log through MCP server."""
        import asyncio
        from mcp.server import MCPServer

        server = MCPServer()

        async def test():
            message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "memory.log",
                    "arguments": {
                        "event": "Test error",
                        "detail": "Something went wrong during testing",
                        "hint": "Check the test setup"
                    }
                }
            }

            response = await server.handle_message(message)

            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 2)
            self.assertIn("result", response)
            self.assertEqual(response["result"], {"ok": True})

        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
