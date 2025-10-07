# Test Development & QA (OLCIA)

Testing focused on reliability with RAG context and MCP automation.

## Plan (7 steps)

1) 🎯 Define targets and metrics (coverage, critical paths)
2) 🔍 `analyze_project_context("tech_stack"|"architecture")` – strategy context
3) 🧪 Tests: unit, integration, E2E (happy path, edge cases, error handling)
4) 🧱 Fixtures/mocks – minimal and appropriate
5) 🚦 Iterate tests with tight feedback loop
6) 📈 Coverage & timings – optimize slow tests
7) 📝 `memory.log` + `add_knowledge` – capture patterns/problems

## Acceptance criteria

- ≥80% coverage for the target module
- Tests are fast, deterministic, non-flaky
- Edge cases and errors covered
- CI/CD green; no warnings

## Commands

```bash
# Project context
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_project_context","arguments":{"analysis_type":"tech_stack"}}}' | python .cursor/mcp/server.py

# Tests
pytest tests/ -v
pytest tests/ --cov=. --cov-report=term-missing
ruff check .
mypy . --strict
```

## Tips

- Design tests for maintainability and speed (avoid shared global state)
- Mock external integrations, but test real logic
- Document complex scenarios with short docstrings