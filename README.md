# MCP+RAG Scaffolding

[![CI](https://github.com/yourusername/olciamcp/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/olciamcp/actions/workflows/ci.yml)

Windows-first Model Context Protocol server with ChromaDB integration for knowledge management and retrieval-augmented generation.

## 🏗️ Architecture

- **MCP Server**: Handles stdio protocol communication with Cursor
- **ChromaDB**: Local vector database for knowledge storage
- **Sentence Transformers**: Embedding generation for semantic search
- **PowerShell Bootstrap**: Windows-native environment setup

## 📁 Repository Structure

```
├── .cursor/
│   ├── mcp.json          # MCP server configuration
│   └── rules/
│       └── agent.mdc     # Development workflow gates
├── knowledge/            # Knowledge base documents
├── memory/               # Conversation memory storage
├── mcp/
│   └── server.py         # MCP server implementation
├── rag/
│   └── store/            # ChromaDB vector storage
├── scripts/
│   └── bootstrap.ps1     # Environment setup script
└── tests/                # Test suites
```

## 🚀 Windows Quick Start

### Prerequisites
- Windows 10/11
- Python 3.11+ (from [python.org](https://python.org))
- pipx (for Poetry installation)

### Setup Environment

1. **Install Poetry:**
   ```powershell
   pipx install poetry==1.7.1
   ```

2. **Install dependencies and create virtual environment:**
   ```powershell
   poetry lock
   poetry install --no-interaction --no-ansi
   ```

3. **Verify installation:**
   ```powershell
   poetry run python -V
   poetry run python -c "import chromadb, mcp; print('✅ Dependencies ready')"
   ```

### Validate Setup

Run these commands to ensure everything works:

```powershell
# Test Python version
poetry run python -V

# Test virtual environment
poetry run python -c "import sys; print(f'Python: {sys.version}')"

# Test MCP server (should start without errors)
poetry run python mcp/server.py <nul
# (Ctrl+C to stop)
```

### End-to-End Demo

Test the complete system with this E2E workflow:

```powershell
# 1. Ingest sample documents
python rag/ingest.py --paths knowledge/

# 2. Query the knowledge base via MCP
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "rag.search", "arguments": {"query": "RAG system architecture", "k": 2}}}' | python mcp/server.py

# 3. Route a development goal
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "orchestrator.route", "arguments": {"goal": "Implement user authentication API"}}}' | python mcp/server.py

# 4. Log a lesson learned
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "memory.log", "arguments": {"event": "Database timeout issue", "detail": "ChromaDB timed out on first query", "hint": "Pre-initialize embeddings"}}}' | python mcp/server.py
```

## 🐳 Docker Quick Start

For containerized development and testing:

### Prerequisites
- Docker Desktop installed and running
- Docker Compose V2

### Run with Docker Compose

1. **Build and start the service:**
   ```bash
   docker compose up --build
   ```

2. **Test the MCP server interactively:**
   ```bash
   # In another terminal, test JSON-RPC communication
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | docker compose exec -T mcp python mcp/server.py
   ```

3. **Stop the service:**
   ```bash
   docker compose down
   ```

### Volume Mounts

The Docker Compose setup mounts:
- `./knowledge/` → `/app/knowledge/` (knowledge base documents)
- `./rag/store/` → `/app/rag/store/` (ChromaDB vector storage)

Changes to local files are reflected immediately in the container.

## 🛠️ Usage

### MCP Tools Available

The server provides these tools through Cursor:

- **`add_knowledge`**: Store content in knowledge base
- **`search_knowledge`**: Retrieve relevant information
- **`add_memory`**: Store conversation context
- **`search_memory`**: Find related conversation history

### Development Workflow

Follow the structured development approach:

1. **Plan**: Create task lists for complex work
2. **Code**: Implement following established patterns
3. **Test**: Validate functionality and run linters
4. **Review**: Ensure minimal diffs and proper documentation

### Configuration

Create `.env` file for custom settings:

```env
# ChromaDB settings
CHROMA_SERVER_HOST=localhost
CHROMA_SERVER_HTTP_PORT=8000

# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## 🔧 Development

### Adding New Tools

1. Define tool in `MCPServer.tools`
2. Implement handler in `MCPServer.call_tool()`
3. Update RAG server methods as needed
4. Test through MCP protocol

### Testing

Run tests with:
```powershell
poetry run pytest tests/
```

Run quality checks:
```powershell
poetry run ruff check .
poetry run mypy . --strict
```

### CI/CD

The project uses GitHub Actions for continuous integration with three automated jobs:

- **Lint + Unit**: Runs Ruff, MyPy, and unit tests (excluding E2E)
- **Docker Build**: Builds the Docker image to ensure it compiles
- **E2E**: Runs end-to-end tests in containerized environment

#### Re-running CI

To manually trigger CI checks:

1. **Via GitHub UI**: Go to Actions tab → Select workflow → "Run workflow"
2. **Via git push**: Push new commits to trigger automatic runs
3. **Via PR**: Open/update a pull request to trigger checks

CI runs automatically on pushes to `main`/`develop` branches and pull requests.

### Code Quality

- Use PowerShell for Windows operations
- Follow Plan→Code→Test→Review workflow
- Keep changes atomic and minimal
- No secrets in version control

## 📋 Acceptance Criteria

✅ `pwsh -File scripts/bootstrap.ps1` succeeds
✅ `python -V` shows Python version
✅ Virtual environment activates correctly
✅ Repo structure matches documentation
✅ MCP server starts without errors

## 🔒 Security

- No secrets committed to VCS
- Use `.env` for sensitive configuration
- `.cursorignore` excludes sensitive files
- Local ChromaDB storage only

## 🎯 Agent Orchestrator

The MCP server includes an intelligent agent routing system that automatically assigns tasks to specialized agents based on goal analysis.

### Available Agents

#### **General Agent**
- **Purpose**: Handles general coding tasks, file operations, and project management
- **Capabilities**: Code creation, refactoring, documentation, architecture design
- **Routing Keywords**: create, implement, write, edit, modify, refactor, optimize, document
- **RAG Integration**: Yes

#### **Tests Agent**
- **Purpose**: Specializes in testing, quality assurance, and test-driven development
- **Capabilities**: Unit tests, integration tests, test coverage, mocking, fixtures
- **Routing Keywords**: test, testing, unittest, pytest, assert, mock, coverage, tdd
- **RAG Integration**: Yes

#### **Database Agent**
- **Purpose**: Handles database operations, schema design, and data management
- **Capabilities**: SQL queries, migrations, ORM models, data constraints, optimization
- **Routing Keywords**: database, sql, query, table, schema, migration, model, orm
- **RAG Integration**: Yes

### Routing Logic

The orchestrator analyzes goal descriptions using:

1. **Keyword Matching**: Identifies domain-specific terms (0-60% score weight)
2. **Pattern Recognition**: Matches common task patterns with regex (0-40% score weight)
3. **Confidence Scoring**: Assigns tasks to highest-scoring agent (0-100% confidence)

### Usage Examples

**Route a testing task:**
```json
{
  "name": "orchestrator.route",
  "arguments": {
    "goal": "Write comprehensive unit tests for the user authentication module"
  }
}
```
*Returns:* `{"agent": "tests", "confidence": 0.85, "steps": [...]}`

**Route a database task:**
```json
{
  "name": "orchestrator.route",
  "arguments": {
    "goal": "Design database schema for e-commerce product catalog",
    "meta": {"context": "backend", "framework": "sqlalchemy"}
  }
}
```
*Returns:* `{"agent": "db", "confidence": 0.92, "steps": [...]}`

### Extension

To add new agents, modify `mcp/orchestrator.py`:

1. Add new `AgentType` enum value
2. Define `AgentCapability` with keywords and patterns
3. Update `AGENT_CAPABILITIES` dictionary
4. Optionally customize routing logic in `AgentRouter._analyze_goal()`

## 🔧 Troubleshooting

### Windows-Specific Issues

**PowerShell Execution Policy**
```powershell
# If scripts fail to run, check execution policy
Get-ExecutionPolicy
# Set to allow local scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Virtual Environment Issues**
```powershell
# If activation fails, try:
.\venv\Scripts\Activate.ps1
# Or use full path:
& "C:\Path\To\Project\venv\Scripts\Activate.ps1"
```

**ChromaDB Initialization Errors**
- Ensure write permissions to `rag/store/` directory
- Check available disk space (ChromaDB needs ~100MB free)
- Try deleting `rag/store/` and re-running ingestion

**Memory/Reflection File Permissions**
- Ensure write access to `memory/` directory
- Check antivirus exclusions for JSONL files

### Common MCP Server Issues

**Server Won't Start**
```bash
# Check for import errors
python -c "import mcp.server; print('Imports OK')"
# Verify all dependencies
pip list | grep -E "(chromadb|sentence|tiktoken)"
```

**Tool Calls Fail**
```bash
# Test individual components
python rag/ingest.py --paths knowledge/
python -c "from mcp.orchestrator import route_goal; print(route_goal('test'))"
```

**Search Returns Empty Results**
- Run ingestion first: `python rag/ingest.py --paths knowledge/`
- Check ChromaDB files exist in `rag/store/`
- Verify embeddings were generated (check logs for "Batches:" output)

### Development Issues

**Tests Fail on Fresh Clone**
```bash
# Ensure clean environment
poetry install
poetry run pytest tests/ -v
```

**Quality Gates Fail**
```bash
# Run individual checks
poetry run ruff check .
poetry run mypy . --strict
poetry run pytest tests/
```

**Path Issues on Windows**
- Use `pathlib.Path` for all file operations
- Avoid hard-coded `/` separators, use `os.path.join()` or Path operations
- Test with both relative and absolute paths

### Performance Issues

**Slow First Query**
- ChromaDB initializes lazily - first query may take 5-10 seconds
- Consider keeping MCP server running for better responsiveness

**High Memory Usage**
- Sentence Transformers model uses ~100MB RAM
- Close other applications if memory constrained
- Consider CPU-only mode (already configured)

**Large File Processing**
- Files >50MB are skipped by default
- Increase limit in `rag/config.yaml` if needed
- Split large documents manually for better chunking

## 🤝 Contributing

1. Follow the development workflow gates
2. Keep Windows-first approach
3. Test on Windows PowerShell
4. Update documentation for changes
