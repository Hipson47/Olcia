# Code Refactoring (OLCIA)

Refactor to improve clarity and maintainability, preserving behavior, with automatic RAG context and quality control.

## Plan (6 steps)

1) 🔍 Context: `auto_context_search(task_type="refactor")` + `analyze_project_context("patterns")`
2) 🗺️ Scope: minimal diff, no public API changes
3) 🛠️ Incremental changes, clear names, early returns, avoid unnecessary try/except
4) 🧪 Tests: establish baseline, then iterate on target tests
5) 💡 `suggest_improvements` – ensure security/maintainability/performance
6) 📝 `memory.log` + `add_knowledge` – capture patterns and lessons

## Acceptance criteria

- No behavior change; tests pass
- Readability/maintainability improved
- Lint/type/tests green
- Patterns documented in KB

## Commands

### Pre-Refactoring Baseline Establishment
```bash
# Baseline
pytest -v --tb=short
ruff check .
mypy . --strict

# RAG context
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"auto_context_search","arguments":{"task_description":"[refactor area]","task_type":"refactor"}}}' | python .cursor/mcp/server.py

echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"analyze_project_context","arguments":{"analysis_type":"patterns"}}}' | python .cursor/mcp/server.py

# Review after changes
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"suggest_improvements","arguments":{"code":"<CHANGED_CODE>","focus_areas":["maintainability","security","performance"]}}}' | python .cursor/mcp/server.py
```

## Tips

- Do not expand scope — aim for minimal diff
- Apply user preferences (`track_user_preferences`) for coding style