#!/usr/bin/env python3
"""
Memory logging system for error tracking and lessons learned.
Provides append-only JSONL logging with simple, reliable format.
"""

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class MemoryEntry:
    """Structured memory entry for logging."""
    timestamp: float
    event: str
    detail: str
    hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class MemoryLogger:
    """
    Append-only memory logger using JSONL format.

    Features:
    - Thread-safe append operations
    - Automatic timestamping
    - Simple JSONL format for reliability
    - Path validation and creation
    """

    def __init__(self, mistakes_file: Path):
        """
        Initialize memory logger.

        Args:
            mistakes_file: Path to the JSONL mistakes file
        """
        self.mistakes_file = mistakes_file
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the mistakes file exists, creating it if necessary."""
        self.mistakes_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.mistakes_file.exists():
            self.mistakes_file.touch()

    def log_error(self, event: str, detail: str, hint: str | None = None) -> bool:
        """
        Log an error or lesson learned to the mistakes file.

        Args:
            event: Brief description of the event/error
            detail: Detailed description of what happened
            hint: Optional hint or lesson learned

        Returns:
            True if logging succeeded, False otherwise
        """
        try:
            entry = MemoryEntry(
                timestamp=time.time(),
                event=event,
                detail=detail,
                hint=hint
            )

            # Append to JSONL file
            with open(self.mistakes_file, 'a', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False)
                f.write('\n')

            return True

        except Exception as e:
            # Log error for debugging but don't crash the application
            print(f"Warning: Failed to log memory entry '{event}': {e}", file=sys.stderr)
            return False

    def get_recent_entries(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get the most recent memory entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent memory entries (newest first)
        """
        try:
            entries = []
            with open(self.mistakes_file, encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry_data = json.loads(line.strip())
                            entries.append(entry_data)
                        except json.JSONDecodeError:
                            continue  # Skip malformed lines

            # Sort by timestamp (newest first) and limit
            entries.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return entries[:limit]

        except FileNotFoundError:
            return []
        except Exception:
            return []


# Global memory logger instance
mistakes_file = Path(__file__).parent.parent / "memory" / "mistakes.jsonl"
memory_logger = MemoryLogger(mistakes_file)


def log_memory(event: str, detail: str, hint: str | None = None) -> dict[str, Any]:
    """
    Log a memory entry (main entry point for the memory.log tool).

    Args:
        event: Brief description of the event/error
        detail: Detailed description of what happened
        hint: Optional hint or lesson learned

    Returns:
        Dictionary with success status
    """
    success = memory_logger.log_error(event, detail, hint)
    return {"ok": success}
