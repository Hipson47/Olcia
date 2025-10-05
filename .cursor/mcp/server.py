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
# Also add the .cursor directory to ensure imports work from different CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))


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
            },
            "auto_context_search": {
                "name": "auto_context_search",
                "description": "Automatically search for relevant context before implementing a task. Returns best practices, similar implementations, and lessons learned.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task to implement"
                        },
                        "task_type": {
                            "type": "string",
                            "description": "Type of task: 'implement', 'debug', 'refactor', or 'test'",
                            "enum": ["implement", "debug", "refactor", "test"]
                        }
                    },
                    "required": ["task_description", "task_type"]
                }
            },
            "suggest_improvements": {
                "name": "suggest_improvements",
                "description": "Analyze code and suggest improvements based on knowledge base and best practices",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to analyze"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Areas to focus on: 'performance', 'security', 'maintainability', 'testing'"
                        }
                    },
                    "required": ["code"]
                }
            },
            "track_user_preferences": {
                "name": "track_user_preferences",
                "description": "Store and retrieve user coding preferences and style",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform: 'store' or 'retrieve'",
                            "enum": ["store", "retrieve"]
                        },
                        "preference_key": {
                            "type": "string",
                            "description": "Preference key (e.g., 'coding_style', 'test_framework', 'language_preference')"
                        },
                        "preference_value": {
                            "type": "string",
                            "description": "Preference value (only for 'store' action)"
                        }
                    },
                    "required": ["action", "preference_key"]
                }
            },
            "analyze_project_context": {
                "name": "analyze_project_context",
                "description": "Analyze current project structure and provide contextual insights",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis: 'architecture', 'dependencies', 'patterns', 'tech_stack'",
                            "enum": ["architecture", "dependencies", "patterns", "tech_stack"]
                        }
                    },
                    "required": ["analysis_type"]
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

        elif tool_name == "auto_context_search":
            task_description = args["task_description"]
            task_type = args["task_type"]
            result = await self.auto_context_search(task_description, task_type)
            return result

        elif tool_name == "suggest_improvements":
            code = args["code"]
            focus_areas = args.get("focus_areas", ["performance", "security", "maintainability"])
            result = await self.suggest_improvements(code, focus_areas)
            return result

        elif tool_name == "track_user_preferences":
            action = args["action"]
            preference_key = args["preference_key"]
            preference_value = args.get("preference_value")
            result = self.track_user_preferences(action, preference_key, preference_value)
            return result

        elif tool_name == "analyze_project_context":
            analysis_type = args["analysis_type"]
            result = await self.analyze_project_context(analysis_type)
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

    async def auto_context_search(self, task_description: str, task_type: str) -> dict[str, Any]:
        """
        Automatically search for relevant context before implementing a task.
        Returns best practices, similar implementations, and lessons learned.
        """
        try:
            # Search knowledge base for similar implementations
            implementations = self.rag_server.search_knowledge(
                f"{task_type} {task_description}",
                n_results=5
            )

            # Search memory for related patterns and lessons
            memory_results = self.rag_server.search_memory(
                task_description,
                n_results=3
            )

            # Search for best practices
            best_practices = self.rag_server.search_knowledge(
                f"best practices {task_type}",
                n_results=3
            )

            return {
                "similar_implementations": implementations,
                "lessons_learned": memory_results,
                "best_practices": best_practices,
                "recommendations": self._generate_recommendations(task_type)
            }

        except Exception as e:
            return {
                "error": str(e),
                "similar_implementations": [],
                "lessons_learned": [],
                "best_practices": []
            }

    async def suggest_improvements(self, code: str, focus_areas: list[str]) -> dict[str, Any]:
        """
        Analyze code and suggest improvements based on knowledge base and best practices.
        """
        try:
            suggestions = []

            for area in focus_areas:
                # Search knowledge base for patterns related to improvement area
                results = self.rag_server.search_knowledge(
                    f"{area} improvements best practices",
                    n_results=3
                )

                if results:
                    suggestions.append({
                        "area": area,
                        "recommendations": [r["content"][:200] for r in results],
                        "relevance_scores": [r["relevance_score"] for r in results]
                    })

            return {
                "suggestions": suggestions,
                "analyzed_areas": focus_areas,
                "code_length": len(code)
            }

        except Exception as e:
            return {
                "error": str(e),
                "suggestions": []
            }

    def track_user_preferences(self, action: str, preference_key: str, preference_value: str | None = None) -> dict[str, Any]:
        """
        Store and retrieve user coding preferences and style.
        """
        try:
            if action == "store":
                if not preference_value:
                    return {"ok": False, "error": "preference_value required for store action"}

                # Store preference in memory collection
                self.rag_server.add_memory(
                    f"User preference: {preference_key} = {preference_value}",
                    context="user_preferences"
                )

                return {
                    "ok": True,
                    "action": "stored",
                    "preference_key": preference_key,
                    "preference_value": preference_value
                }

            elif action == "retrieve":
                # Search memory for the preference
                results = self.rag_server.search_memory(
                    f"User preference: {preference_key}",
                    n_results=1
                )

                if results:
                    return {
                        "ok": True,
                        "action": "retrieved",
                        "preference_key": preference_key,
                        "preference_value": results[0]["content"],
                        "relevance": results[0]["relevance_score"]
                    }
                else:
                    return {
                        "ok": False,
                        "action": "retrieved",
                        "error": "Preference not found"
                    }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    async def analyze_project_context(self, analysis_type: str) -> dict[str, Any]:
        """
        Analyze current project structure and provide contextual insights.
        """
        try:
            # Search knowledge base for project-related patterns
            results = self.rag_server.search_knowledge(
                f"project {analysis_type} patterns",
                n_results=5
            )

            insights = []
            for result in results:
                insights.append({
                    "insight": result["content"][:300],
                    "relevance": result["relevance_score"],
                    "metadata": result.get("metadata", {})
                })

            return {
                "analysis_type": analysis_type,
                "insights": insights,
                "total_findings": len(insights)
            }

        except Exception as e:
            return {
                "error": str(e),
                "insights": []
            }

    def _generate_recommendations(self, task_type: str) -> list[str]:
        """Generate task-specific recommendations."""
        recommendations = {
            "implement": [
                "Start with RAG search for similar implementations",
                "Write tests before/during implementation",
                "Add proper type hints and error handling",
                "Document complex logic with comments"
            ],
            "debug": [
                "Search for similar bugs in memory",
                "Check recent changes that might cause the issue",
                "Add regression tests after fixing",
                "Log the error and solution for future reference"
            ],
            "refactor": [
                "Ensure all tests pass before starting",
                "Make small, incremental changes",
                "Preserve existing behavior",
                "Update documentation and tests"
            ],
            "test": [
                "Cover happy path and edge cases",
                "Test error handling scenarios",
                "Aim for >80% code coverage",
                "Use descriptive test names"
            ]
        }

        return recommendations.get(task_type, ["Follow best practices from knowledge base"])

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
