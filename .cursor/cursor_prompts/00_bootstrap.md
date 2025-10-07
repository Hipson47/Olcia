# Bootstrap MCP+RAG (OLCIA)

Quick-start guide for an always-on OLCIA agent (MCP+RAG) ready to use tools automatically.

### Core Infrastructure
- **Multi-Agent Orchestration**: Specialized agents for different task types
- **Advanced RAG System**: ChromaDB with semantic search and pattern recognition
- **MCP Protocol**: Full stdio/SSE implementation with tool ecosystem
- **Background Processing**: Long-running operations with progress monitoring

- MCP Server (`.cursor/mcp/server.py`) – stdio JSON-RPC, RAG (ChromaDB), Memory
- MCP Tools – including: `auto_context_search`, `suggest_improvements`, `track_user_preferences`, `analyze_project_context`
- Cursor config (`.cursor/mcp.json`)
- Prompts & rules tuned for automatic MCP/RAG usage

## Plan (4 steps)

1) Environment: Python 3.11+, Poetry, `.env` with keys (OPENAI_API_KEY/ANTHROPIC_API_KEY)
2) MCP Server: run and verify initialize/tools list
3) Knowledge ingest: `knowledge/` → RAG (`rag.ingest`)
4) Quality gates: ruff, mypy, pytest

## Acceptance criteria

- `python .cursor/mcp/server.py` starts without errors
- `tools/list` returns 12 tools (including 4 new)
- `rag.ingest` works on `knowledge/`
- ruff/mypy/pytest pass
- MCP in Cursor shows green status

## Commands

```bash
# Bootstrap (Windows PowerShell)
./.cursor/scripts/bootstrap.ps1

# Initialize + tools/list
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cursor","version":"1.0"}}}' | python .cursor/mcp/server.py

echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python .cursor/mcp/server.py

# Ingest knowledge
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"rag.ingest","arguments":{"paths":["knowledge/"]}}}' | python .cursor/mcp/server.py

# Quality gates
ruff check .
mypy . --strict
pytest -v
```

## Tips

- Always begin with `auto_context_search` before starting a task
- Track preferences (`track_user_preferences`) to personalize style
- Add patterns to the KB (`add_knowledge`) after significant decisions