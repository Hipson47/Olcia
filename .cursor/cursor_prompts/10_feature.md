# Feature Implementation (OLCIA)

Add a new feature leveraging MCP+RAG and the assistant's automatic tools.

## Plan (8 steps)

1) 🔍 `auto_context_search` – gather context (similar implementations, best practices, lessons)
2) 🧠 `track_user_preferences(retrieve, ...)` – align with user style
3) 🏗️ Implement – minimal diff, types, validation
4) 💡 `suggest_improvements` – code review (security/perf/maint/testing)
5) 🧪 Tests – unit + integration
6) 📚 Docs – README + KB (`add_knowledge` for patterns)
7) 🔁 E2E with MCP – `tools/list`, `tools/call`
8) ✅ Quality gates – ruff, mypy, pytest

## Acceptance criteria

- Requirements implemented with no regressions
- Quality gates pass
- MCP tools used (at least `auto_context_search` + `suggest_improvements`)
- Patterns added to KB; preferences updated; `memory.log` filled

## Commands

### Knowledge Mining (RAG-Enhanced)
```bash
# Context for the feature
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"auto_context_search","arguments":{"task_description":"[desc]","task_type":"implement"}}}' | python .cursor/mcp/server.py

# Code review
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"suggest_improvements","arguments":{"code":"<CODE>","focus_areas":["security","maintainability","testing"]}}}' | python .cursor/mcp/server.py

# Preferences
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"track_user_preferences","arguments":{"action":"store","preference_key":"coding_style","preference_value":"clean_code"}}}' | python .cursor/mcp/server.py

# Tests
pytest -v
ruff check .
mypy . --strict
```

### Context Limitation (Token Optimization)
```bash
@file:requirements.md @folder:affected_modules
@symbol:existing_integration_points
@cursor-agent route "feature complexity assessment"
```

- Always start with RAG + memory context
- Treat `suggest_improvements` as automated code review
- Document important decisions in KB (`add_knowledge`) and `memory.log`