# Code Refactoring

Improve code quality, maintainability, and performance while preserving all existing functionality.

## Scope

**Refactoring Target:** [Specific code/module/function to refactor]

**Refactoring Type:** [e.g., performance, readability, maintainability, architecture]

**Files to modify:**
- `@[target_file]` - Primary file being refactored
- `@tests/test_[target].py` - Update tests if needed
- `@mcp/server.py` - Update imports/interfaces if changing APIs

**Files to reference:**
- `@.cursor/rules/agent.mdc` - Minimal-diff policy and quality gates
- `@tests/` - Ensure no test regressions
- `@requirements.txt` - Check for new dependencies

## Implementation Plan (6 steps)

1. **Analyze current code** - Understand existing behavior and identify improvement opportunities
2. **Plan refactoring approach** - Design changes that preserve functionality
3. **Implement changes incrementally** - Small, testable changes with frequent verification
4. **Update tests if needed** - Modify test structure without changing test intent
5. **Verify functionality preservation** - Ensure all existing behavior still works
6. **Clean up and document** - Remove technical debt and update documentation

## Acceptance Criteria

- ✅ **Behavior Preservation**: All existing functionality works exactly as before
- ✅ **No Regressions**: All existing tests still pass
- ✅ **Quality Gates**: ruff, mypy, pytest all pass
- ✅ **Performance**: No significant performance degradation (if applicable)
- ✅ **Readability**: Code is more maintainable and understandable
- ✅ **Documentation**: Updated comments and docstrings where improved
- ✅ **Minimal Diff**: Changes are focused and don't touch unrelated code

## Commands to Run

```bash
# Before refactoring - establish baseline
python -m pytest tests/ -v --tb=short
ruff check .
mypy . --strict

# During refactoring - run frequently
python -m pytest tests/test_[target].py -v  # Specific tests
python -c "import [target_module]; print('Import works')"

# After refactoring - full verification
python -m pytest tests/ -v  # All tests
ruff check .
mypy . --strict

# Integration testing
python mcp/server.py  # Ensure MCP server still starts
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python mcp/server.py
```

## Refactoring Guidelines

**DO:**
- Change internal implementation while preserving external interfaces
- Improve variable/function names for clarity
- Break down large functions into smaller, focused ones
- Remove duplicate code and consolidate logic
- Add type hints and improve error handling
- Update documentation and comments

**DO NOT:**
- Change public APIs without explicit approval
- Modify functionality or behavior
- Remove existing features
- Change test expectations (only test structure)
- Introduce new dependencies without approval
- Make broad changes across many files

## Notes

- **Stop immediately** if tests start failing - indicates behavior change
- Use `git diff` to ensure minimal, focused changes
- Document refactoring rationale in commit messages
- Consider performance implications for critical paths
- Update `memory/reflexion.md` with lessons learned from the refactoring
