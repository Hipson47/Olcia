# Bootstrap Project Setup

Initialize a new MCP+RAG project with complete scaffolding and environment setup.

## Recommended AI Model: Claude 3.5 Sonnet

For the main agent controlling the RAG system, **Claude 3.5 Sonnet** is the recommended model because:

### Why Claude 3.5 Sonnet?
- **Superior code understanding** - Better at Python, architecture analysis, and code generation than GPT models
- **Excellent reasoning** - Strong Chain-of-Thought capabilities for decision making
- **Long context window** - Can handle complex RAG contexts and conversation history
- **Cost-effective** - Lower cost per token than GPT-4o while maintaining high quality
- **Agent-friendly** - Designed for tool use and multi-step reasoning tasks

### Integration Points:
- Replace `gpt-4o-mini` in `mcp/orchestrator.py` with `claude-3-5-sonnet-20241022`
- Use Anthropic API instead of OpenAI for main agent decisions
- Keep GPT-4o-mini for lightweight tasks if needed

### Expected Benefits:
- Better code quality and architectural decisions
- More accurate RAG context utilization
- Improved multi-step task planning
- Enhanced error handling and debugging capabilities

## Scope

**Files to create/modify:**
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project configuration
- `README.md` - Project documentation
- `.cursor/` - Cursor IDE configuration
- `mcp/server.py` - MCP server implementation
- `tests/` - Test suite structure
- `scripts/bootstrap.ps1` - Environment setup script

**Folders to create:**
- `knowledge/` - Knowledge base storage
- `memory/` - Error memory and reflections
- `rag/store/` - Vector database storage
- `tests/` - Test files

## Implementation Plan (7 steps)

1. **Create project structure** - Set up directories and basic files
2. **Configure dependencies** - Add Python packages to requirements.txt
3. **Implement MCP server** - Create basic stdio server with tool scaffolding
4. **Add RAG components** - Basic ChromaDB integration and file loading
5. **Create bootstrap script** - PowerShell script for environment setup
6. **Add test infrastructure** - Basic test structure and fixtures
7. **Update documentation** - README and configuration files

## Acceptance Criteria

- ✅ `python mcp/server.py` starts without errors
- ✅ `python -m pytest tests/` discovers and runs tests
- ✅ `scripts/bootstrap.ps1` creates virtual environment
- ✅ All quality gates pass: ruff, mypy, pytest
- ✅ README provides clear setup instructions
- ✅ Project structure matches documented layout

## Commands to Run

```bash
# Quality gates (run after each major change)
ruff check .
mypy . --strict
python -m pytest tests/ -v

# Bootstrap verification
python mcp/server.py  # Should start MCP server
python -c "import chromadb, mcp.server"  # Verify imports work

# Environment setup
./scripts/bootstrap.ps1  # Windows PowerShell
```

## Notes

- Follow Plan→Code→Test→Review workflow gates
- Keep changes minimal and atomic
- Test incrementally after each step
- Stop immediately if quality gates fail
- Document all setup steps clearly in README
