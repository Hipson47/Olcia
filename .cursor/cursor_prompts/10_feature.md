# Feature Implementation

Add a new feature to the MCP+RAG system with complete implementation, testing, and documentation.

## Scope

**Feature Description:** [Brief description of the feature to implement]

**Files to modify/create:**
- `mcp/server.py` - Add new MCP tools or extend existing ones
- `mcp/[feature_module].py` - New feature implementation
- `tests/test_[feature].py` - Feature tests
- `README.md` - Update documentation
- `knowledge/` - Add relevant documentation if needed

**Files to reference:**
- `@mcp/server.py` - Current MCP tool structure
- `@tests/` - Existing test patterns
- `@rag/` - RAG system integration points
- `@requirements.txt` - Dependency management

## Implementation Plan (8 steps)

1. **Analyze requirements** - Understand feature scope and integration points
2. **Design API/interface** - Define MCP tool schemas and function signatures
3. **Implement core logic** - Create feature module with business logic
4. **Add MCP integration** - Wire feature into MCP server tools
5. **Write comprehensive tests** - Unit and integration tests
6. **Update documentation** - README and inline documentation
7. **Test integration** - End-to-end testing with MCP protocol
8. **Quality assurance** - Run all quality gates

## Acceptance Criteria

- ✅ Feature implements specified requirements completely
- ✅ New MCP tools follow JSON-RPC schema standards
- ✅ All tests pass including new feature tests
- ✅ Quality gates pass: ruff, mypy, pytest
- ✅ Documentation updated with usage examples
- ✅ Feature integrates cleanly with existing RAG system
- ✅ No regressions in existing functionality
- ✅ MCP server starts and serves new tools correctly

## Commands to Run

```bash
# Development workflow
python -m pytest tests/ -v  # Run tests after each major change
ruff check .               # Code quality check
mypy . --strict           # Type checking

# Feature testing
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python mcp/server.py
# Should show new tool in the list

# Specific feature testing
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "[new_tool]", "arguments": {...}}}' | python mcp/server.py

# Full integration test
python -m pytest tests/test_[feature].py -v
```

## Notes

- Follow strict Plan→Code→Test→Review workflow
- Keep changes minimal and atomic - one feature at a time
- Add comprehensive error handling and logging
- Update memory/reflexion.md with lessons learned
- Test on Windows PowerShell environment
- Document any new dependencies or configuration requirements
