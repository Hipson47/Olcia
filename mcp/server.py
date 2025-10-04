#!/usr/bin/env python3
"""
MCP+RAG Server
Windows-first MCP server with ChromaDB integration for knowledge management.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import chromadb
    from chromadb.config import Settings
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer

    from mcp.memory import log_memory
    from mcp.orchestrator import route_goal
    from rag.ingest import RAGIngestor
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    sys.exit(1)

# Load environment variables
load_dotenv()


class SimpleRateLimiter:
    """Simple token bucket rate limiter for API protection."""

    def __init__(self, requests_per_minute: int = 60) -> None:
        self.requests_per_minute = requests_per_minute
        self.requests: list[float] = []
        self.lock = asyncio.Lock()

    async def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit."""
        async with self.lock:
            current_time = time.time()

            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests
                           if current_time - req_time < 60]

            # Check if under limit
            if len(self.requests) < self.requests_per_minute:
                self.requests.append(current_time)
                return True

            return False


class RAGServer:
    def __init__(self) -> None:
        self.store_path = Path("rag/store")
        self.store_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.store_path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Create or get collections
        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "General knowledge and documentation"}
        )

        self.memory_collection = self.client.get_or_create_collection(
            name="conversation_memory",
            metadata={"description": "Conversation context and memory"}
        )

    def get_embedding(self, text: str) -> list[float]:
        """Generate embedding for text."""
        return self.embedding_model.encode(text).tolist()

    def add_knowledge(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """Add content to knowledge base."""
        if metadata is None:
            metadata = {}

        # Convert all metadata values to strings for ChromaDB compatibility
        string_metadata = {key: str(value) for key, value in metadata.items()}

        embedding = self.get_embedding(content)
        doc_id = f"doc_{len(self.knowledge_collection.get()['ids']) + 1}"

        self.knowledge_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[string_metadata],
            ids=[doc_id]
        )

        return doc_id

    def search_knowledge(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Search knowledge base for relevant content."""
        query_embedding = self.get_embedding(query)

        results = self.knowledge_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        # Format results
        formatted_results = []
        for _i, (_doc_id, document, metadata, distance) in enumerate(zip(
            results['ids'][0] if results['ids'] else [],
            results['documents'][0] if results['documents'] else [],
            results['metadatas'][0] if results['metadatas'] else [],
            results['distances'][0] if results['distances'] else [], strict=False
        )):
            formatted_results.append({
                "id": _doc_id,
                "content": document,
                "metadata": metadata,
                "relevance_score": 1.0 - distance  # Convert distance to similarity score
            })

        return formatted_results

    def search_knowledge_chunks(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """Search knowledge base and return chunks with text, path, idx, score."""
        query_embedding = self.get_embedding(query)

        results = self.knowledge_collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        # Format results as chunks
        chunks = []
        for _i, (_doc_id, document, metadata, distance) in enumerate(zip(
            results['ids'][0] if results['ids'] else [],
            results['documents'][0] if results['documents'] else [],
            results['metadatas'][0] if results['metadatas'] else [],
            results['distances'][0] if results['distances'] else [], strict=False
        )):
            chunks.append({
                "text": document,
                "path": metadata.get("source_file", ""),
                "idx": metadata.get("chunk_index", 0),
                "score": 1.0 - distance  # Convert distance to similarity score
            })

        return chunks

    def add_memory(self, content: str, context: str = "general") -> str:
        """Add content to conversation memory."""
        embedding = self.get_embedding(content)
        mem_id = f"mem_{len(self.memory_collection.get()['ids']) + 1}"

        self.memory_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"context": context, "timestamp": str(asyncio.get_event_loop().time())}],
            ids=[mem_id]
        )

        return mem_id

    def search_memory(self, query: str, n_results: int = 3) -> list[dict[str, Any]]:
        """Search conversation memory."""
        query_embedding = self.get_embedding(query)

        results = self.memory_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        formatted_results = []
        for _i, (mem_id, document, metadata, distance) in enumerate(zip(
            results['ids'][0] if results['ids'] else [],
            results['documents'][0] if results['documents'] else [],
            results['metadatas'][0] if results['metadatas'] else [],
            results['distances'][0] if results['distances'] else [], strict=False
        )):
            formatted_results.append({
                "id": mem_id,
                "content": document,
                "metadata": metadata,
                "relevance_score": 1.0 - distance
            })

        return formatted_results

class MCPServer:
    def __init__(self) -> None:
        self.rag_server = RAGServer()
        self.rag_ingestor: Optional[RAGIngestor] = None  # Lazy initialization
        self.rate_limiter = SimpleRateLimiter(requests_per_minute=120)  # 120 requests per minute
        self.tools = {
            "add_knowledge": {
                "name": "add_knowledge",
                "description": "Add content to the knowledge base for future retrieval",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to add to knowledge base"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata for the content",
                            "additionalProperties": True
                        }
                    },
                    "required": ["content"]
                }
            },
            "search_knowledge": {
                "name": "search_knowledge",
                "description": "Search the knowledge base for relevant information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            "add_memory": {
                "name": "add_memory",
                "description": "Add content to conversation memory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to add to memory"
                        },
                        "context": {
                            "type": "string",
                            "description": "Context category for the memory",
                            "default": "general"
                        }
                    },
                    "required": ["content"]
                }
            },
            "search_memory": {
                "name": "search_memory",
                "description": "Search conversation memory for relevant context",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            },
            "rag.search": {
                "name": "rag.search",
                "description": "Search the RAG knowledge base for relevant content chunks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant content"
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            "rag.ingest": {
                "name": "rag.ingest",
                "description": "Ingest files into the RAG knowledge base",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of file or directory paths to ingest (default: knowledge/)"
                        }
                    }
                }
            },
            "orchestrator.route": {
                "name": "orchestrator.route",
                "description": "Route a goal to the most appropriate specialized agent",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal or task description to route to an agent"
                        },
                        "meta": {
                            "type": "object",
                            "description": "Optional metadata about the context or requirements",
                            "additionalProperties": True
                        }
                    },
                    "required": ["goal"]
                }
            },
            "memory.log": {
                "name": "memory.log",
                "description": "Log an error or lesson learned to the memory system",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event": {
                            "type": "string",
                            "description": "Brief description of the event or error"
                        },
                        "detail": {
                            "type": "string",
                            "description": "Detailed description of what happened"
                        },
                        "hint": {
                            "type": "string",
                            "description": "Optional hint or lesson learned"
                        }
                    },
                    "required": ["event", "detail"]
                }
            }
        }

    async def handle_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Handle incoming MCP messages."""
        # Check rate limit
        if not await self.rate_limiter.is_allowed():
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32001,
                    "message": "Rate limit exceeded. Please wait before making more requests."
                }
            }

        msg_id = message.get("id")
        method = message.get("method")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "rag-server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": list(self.tools.values())
                }
            }

        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            try:
                result = await self.call_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": result
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

    async def call_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool with given arguments."""
        if tool_name == "add_knowledge":
            doc_id = self.rag_server.add_knowledge(
                args["content"],
                args.get("metadata", {})
            )
            return {"document_id": doc_id, "status": "added"}

        elif tool_name == "search_knowledge":
            results = self.rag_server.search_knowledge(
                args["query"],
                args.get("n_results", 5)
            )
            return {"results": results}

        elif tool_name == "add_memory":
            mem_id = self.rag_server.add_memory(
                args["content"],
                args.get("context", "general")
            )
            return {"memory_id": mem_id, "status": "added"}

        elif tool_name == "search_memory":
            results = self.rag_server.search_memory(
                args["query"],
                args.get("n_results", 3)
            )
            return {"results": results}

        elif tool_name == "rag.search":
            chunks = self.rag_server.search_knowledge_chunks(
                args["query"],
                args.get("k", 5)
            )
            return {"chunks": chunks}

        elif tool_name == "rag.ingest":
            paths = args.get("paths", ["knowledge/"])
            result = self.ingest_files(paths)
            return result

        elif tool_name == "orchestrator.route":
            goal = args["goal"]
            meta = args.get("meta")
            result = route_goal(goal, meta)
            return result

        elif tool_name == "memory.log":
            event = args["event"]
            detail = args["detail"]
            hint = args.get("hint")
            result = log_memory(event, detail, hint)
            return result

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def ingest_files(self, paths: list[str]) -> dict[str, Any]:
        """Ingest files into the RAG knowledge base."""
        try:
            # Initialize ingestor if needed
            if self.rag_ingestor is None:
                self.rag_ingestor = RAGIngestor(persist_directory="rag/store")

            total_count = 0
            all_successful = True

            for path_str in paths:
                path = Path(path_str)

                if path.is_file():
                    result = self.rag_ingestor.ingest_file(path)
                    if result.get("status") == "success":
                        total_count += result.get("chunks_count", 0)
                    else:
                        all_successful = False
                elif path.is_dir():
                    results = self.rag_ingestor.ingest_directory(path)
                    for result in results:
                        if result.get("status") == "success":
                            total_count += result.get("chunks_count", 0)
                        else:
                            all_successful = False
                else:
                    all_successful = False

            return {
                "ok": all_successful,
                "count": total_count
            }

        except Exception as e:
            return {
                "ok": False,
                "count": 0,
                "error": str(e)
            }

async def main() -> None:
    """Main MCP server loop."""
    server = MCPServer()

    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
            response = await server.handle_message(message)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"}
            }), flush=True)
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
