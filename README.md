# MCP+RAG Scaffolding with AI Agent Orchestration

🚀 **Next-Generation AI-Powered Development Environment**

Windows-first Model Context Protocol server with ChromaDB integration, GPT-4o-mini AI agents, and intelligent task routing using Chain-of-Thought reasoning.

## 🏗️ Architecture

- **🤖 AI Agent Orchestrator**: GPT-4o-mini powered intelligent task routing with Chain-of-Thought reasoning
- **🧠 RAG Integration**: Retrieval-Augmented Generation with ChromaDB for context-aware responses
- **🔄 MCP Server**: Advanced stdio protocol communication with Cursor
- **💾 ChromaDB**: Local vector database for knowledge and memory storage
- **🔍 Semantic Search**: Sentence Transformers for intelligent content retrieval
- **⚡ PowerShell Bootstrap**: Windows-native environment setup with Poetry

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
- **OpenAI API Key** (for AI agent functionality)
- At least 4GB RAM (recommended for AI processing)

### Setup Environment

1. **Install Poetry:**
   ```powershell
   pipx install poetry==1.7.1
   ```

2. **Configure OpenAI API Key:**
   ```powershell
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. **Generate lock file and install dependencies:**
   ```powershell
   # Generate poetry.lock from pyproject.toml
   poetry lock

   # Install dependencies in virtual environment (includes OpenAI)
   poetry install --no-interaction --no-ansi
   ```

4. **Verify installation:**
   ```powershell
   # Check Python version in virtual environment
   poetry run python -V

   # Test core imports
   poetry run python -c "import chromadb, mcp, openai; print('✅ Dependencies ready')"

   # Test AI agent functionality
   poetry run python -c "from mcp.orchestrator import route_goal_async; import asyncio; result = asyncio.run(route_goal_async('test task')); print('✅ AI agents ready' if result['agent'] else '❌ AI agents failed')"
   ```

5. **Run local tests:**
   ```powershell
   # Run unit tests (excluding E2E)
   poetry run pytest tests/ -m "not e2e" --tb=short

   # Run linting and type checking
   poetry run ruff check .
   poetry run mypy . --strict
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

### 🤖 AI Agent Demo

Test the revolutionary AI-powered system with intelligent task routing:

```powershell
# 1. Ingest knowledge base (provides context for AI agents)
python rag/ingest.py --paths knowledge/

# 2. Test AI-powered task routing with Chain-of-Thought reasoning
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "orchestrator.route", "arguments": {"goal": "Implement JWT authentication for REST API with refresh tokens"}}}' | python mcp/server.py

# 3. Test semantic search with RAG integration
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "rag.search", "arguments": {"query": "authentication security best practices", "k": 3}}}' | python mcp/server.py

# 4. Route testing task with AI analysis
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "orchestrator.route", "arguments": {"goal": "Create comprehensive test suite for user registration with TDD"}}}' | python mcp/server.py

# 5. Log development insights (AI agents learn from experience)
echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "memory.log", "arguments": {"event": "JWT implementation success", "detail": "AI agent provided excellent step-by-step guidance", "hint": "Use AI routing for complex authentication tasks"}}}' | python mcp/server.py
```

### 🎯 Expected AI Agent Responses

**JWT Authentication Routing:**
```json
{
  "agent": "general",
  "confidence": 0.92,
  "reasoning": "JWT authentication involves API development, security patterns, and token management...",
  "steps": [
    "Analyze authentication requirements and security constraints",
    "Design JWT token structure with claims and expiration",
    "Implement token generation and validation logic",
    "Create authentication middleware for route protection",
    "Implement refresh token rotation for security",
    "Add proper error handling and logging"
  ]
}
```

**Testing Task Routing:**
```json
{
  "agent": "tests",
  "confidence": 0.95,
  "reasoning": "The task explicitly mentions testing, TDD approach, and test suite creation...",
  "steps": [
    "Analyze existing codebase and identify testable components",
    "Set up testing framework and directory structure",
    "Write failing tests for user registration functionality",
    "Implement registration logic to pass tests",
    "Add edge case testing and error scenarios",
    "Set up CI/CD integration for automated testing"
  ]
}
```

### Automated E2E Scripts

For automated end-to-end testing on Windows:

**PowerShell (Recommended):**
```powershell
# Run complete E2E test (ingestion + JSON-RPC query)
pwsh .\scripts\e2e.ps1
```

**Batch File (Fallback):**
```batch
# Run complete E2E test (ingestion + JSON-RPC query)
.\scripts\e2e.bat
```

Both scripts automatically:
- Create/verify test knowledge document (`knowledge/e2e.md`)
- Run document ingestion pipeline
- Test JSON-RPC search functionality
- Validate responses and report results

## 🐳 Docker Quick Start

For containerized development and testing:

### Prerequisites
- Docker Desktop installed and running
- Docker Compose V2

### Using Docker Compose

1. **Build and start the service:**
   ```bash
   docker compose up --build
   ```

2. **Test the MCP server interactively:**
   ```bash
   # In another terminal, test JSON-RPC communication
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | docker compose exec -T mcp python mcp/server.py
   ```

3. **Run E2E tests in container:**
   ```bash
   docker compose exec mcp bash /app/scripts/ci_e2e_test.sh
   ```

4. **Stop the service:**
   ```bash
   docker compose down
   ```

### Direct Docker Usage

For one-off testing without compose:

```bash
# Build the image
docker build -t mcp-rag:latest .

# Run with volume mounts
docker run --rm -v "$(pwd)/knowledge:/app/knowledge" -v "$(pwd)/rag/store:/app/rag/store" mcp-rag:latest python -c "
import sys
sys.path.insert(0, '.')
from rag.ingest import RAGIngestor
ingestor = RAGIngestor(persist_directory='store')
result = ingestor.ingest_directory('knowledge')
print(f'Ingestion: {result}')
"

# Test JSON-RPC
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"rag.search","arguments":{"query":"MCP system","k":2}}}' | \
docker run -i --rm -v "$(pwd)/knowledge:/app/knowledge" -v "$(pwd)/rag/store:/app/rag/store" mcp-rag:latest python mcp/server.py
```

### Volume Mounts

The Docker setup mounts:
- `./knowledge/` → `/app/knowledge/` (knowledge base documents)
- `./rag/store/` → `/app/rag/store/` (ChromaDB vector storage)

Changes to local files are reflected immediately in the container.

## 🛠️ Usage

### MCP Tools Available

The server provides these AI-enhanced tools through Cursor:

#### **Core RAG Tools**
- **`add_knowledge`**: Store content in knowledge base with semantic embeddings
- **`search_knowledge`**: Retrieve relevant information with relevance scoring
- **`add_memory`**: Store conversation context and lessons learned
- **`search_memory`**: Find related conversation history with context

#### **AI Agent Tools**
- **`rag.search`**: Advanced semantic search with knowledge integration
- **`rag.ingest`**: Intelligent document ingestion with chunking optimization
- **`orchestrator.route`**: 🤖 **AI-powered task routing** with GPT-4o-mini reasoning
- **`memory.log`**: Log development insights and error patterns

#### **Enhanced Capabilities**
- **Chain-of-Thought Reasoning**: AI agents use structured reasoning for complex tasks
- **Dynamic Specialization**: Agents adapt expertise based on task requirements
- **Context-Aware Responses**: RAG integration provides relevant knowledge during execution

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

#### Jobs Overview

- **🔍 Lint + Unit** (`lint_unit`): Quality assurance for Python code
  - Runs Ruff linter for code style and errors
  - Executes MyPy type checker for static analysis
  - Runs unit tests (excluding E2E) with pytest
  - Uses Poetry for dependency management

- **🐳 Docker Build** (`docker_build`): Container validation
  - Builds Docker image from `Dockerfile`
  - Verifies image creation and basic functionality
  - Ensures containerized environment works

- **🧪 E2E Tests** (`e2e`): Full pipeline validation
  - Builds Docker image with E2E tag
  - Creates sample knowledge document
  - Runs document ingestion pipeline
  - Tests JSON-RPC communication with search queries
  - Validates response format and content

#### CI Status


#### Re-running CI

To manually trigger CI checks:

1. **Via GitHub UI**: Go to Actions tab → Select workflow → "Run workflow"
2. **Via git push**: Push new commits to trigger automatic runs
3. **Via PR**: Open/update a pull request to trigger checks

CI runs automatically on:
- Pushes to `main`/`develop` branches
- Pull requests targeting `main`/`develop` branches

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

## 🔒 Security & Privacy

### Core Security Principles
- **Zero Data Retention**: AI agents don't store or learn from your code
- **Local Processing**: All ChromaDB data stored locally on your machine
- **Secure API Keys**: OpenAI keys stored securely in `.env` file
- **No VCS Secrets**: Automated detection prevents committing sensitive data

### AI Agent Security
- **Rate Limiting**: 120 requests/minute protection against abuse
- **Input Validation**: All inputs validated before AI processing
- **Error Handling**: Graceful degradation if AI services unavailable
- **Audit Logging**: All agent interactions logged for transparency

### Environment Security
```env
# Required: Your OpenAI API key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: AI agent configuration
AI_AGENT_MODEL=gpt-4o-mini
AI_AGENT_TEMPERATURE=0.3
AI_AGENT_MAX_TOKENS=1000
```

### Privacy Protection
- **Workspace Trust**: Explicit permission required for AI operations
- **Local Knowledge Base**: All context data processed locally
- **No External Data Sharing**: AI responses stay within your environment
- **Transparent Processing**: Clear visibility into AI decision-making

## 🎯 AI Agent Orchestrator 🤖

The MCP server features a revolutionary AI-powered agent routing system using **GPT-4o-mini** with **Chain-of-Thought reasoning** and **RAG integration** for intelligent task assignment and execution guidance.

### 🤖 AI-Powered Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ User Goal   │───▶│ GPT-4o-mini     │───▶│ RAG Context     │
│ Description │    │ Chain-of-Thought │    │ Knowledge Base  │
└─────────────┘    └─────────────────┘    └─────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Agent       │◀───│ Dynamic Routing │───▶│ Implementation  │
│ Assignment  │    │ & Reasoning     │    │ Steps & Best    │
│ (GENERAL/   │    │                 │    │ Practices       │
│  TESTS/DB)  │    └─────────────────┘    └─────────────────┘
└─────────────┘
```

### Available AI Agents

#### **🤖 General Agent** (AI-Powered)
- **Purpose**: Intelligent general-purpose coding with LLM reasoning
- **Capabilities**: Architecture design, API development, refactoring, documentation
- **AI Features**: Context-aware code generation, pattern recognition, best practices integration
- **RAG Integration**: Full access to knowledge base for informed decisions

#### **🧪 Tests Agent** (AI-Powered)
- **Purpose**: Advanced testing strategies with AI-driven analysis
- **Capabilities**: TDD, coverage optimization, mocking strategies, integration testing
- **AI Features**: Test case generation, coverage analysis, assertion optimization
- **RAG Integration**: Access to testing best practices and patterns

#### **💾 Database Agent** (AI-Powered)
- **Purpose**: Intelligent database design and optimization
- **Capabilities**: Schema design, migrations, query optimization, data modeling
- **AI Features**: Performance optimization, relationship modeling, indexing strategies
- **RAG Integration**: Database best practices and architectural patterns

### 🧠 Chain-of-Thought Reasoning Process

The AI orchestrator uses structured reasoning:

1. **Goal Analysis**: Deep understanding of technical requirements and constraints
2. **Domain Assessment**: Evaluation of required expertise (frontend, backend, testing, database)
3. **RAG Context Retrieval**: Search for relevant knowledge and best practices
4. **Agent Matching**: Dynamic specialization based on task complexity and requirements
5. **Step Generation**: Creation of actionable, context-aware implementation steps
6. **Confidence Scoring**: LLM-based confidence assessment (0.0-1.0)

### 💡 Intelligent Routing Examples

**Route authentication implementation:**
```json
{
  "name": "orchestrator.route",
  "arguments": {
    "goal": "Implement JWT authentication for REST API with refresh tokens"
  }
}
```
*Returns:*
```json
{
  "agent": "general",
  "confidence": 0.92,
  "reasoning": "JWT authentication involves API development, security patterns, and token management. The task requires understanding of authentication flows, security best practices, and REST API design. Based on the technical domain analysis, this falls under general-purpose development with security considerations.",
  "steps": [
    "Analyze authentication requirements and security constraints",
    "Design JWT token structure with claims and expiration",
    "Implement token generation and validation logic",
    "Create authentication middleware for route protection",
    "Implement refresh token rotation for security",
    "Add proper error handling and logging"
  ]
}
```

**Route testing task:**
```json
{
  "name": "orchestrator.route",
  "arguments": {
    "goal": "Create comprehensive test suite for user registration with TDD approach"
  }
}
```
*Returns:*
```json
{
  "agent": "tests",
  "confidence": 0.95,
  "reasoning": "The task explicitly mentions testing, TDD approach, and test suite creation. This clearly falls under testing specialization with focus on comprehensive coverage and test-driven development methodology.",
  "steps": [
    "Analyze existing codebase and identify testable components",
    "Set up testing framework and directory structure",
    "Write failing tests for user registration functionality",
    "Implement registration logic to pass tests",
    "Add edge case testing and error scenarios",
    "Set up CI/CD integration for automated testing"
  ]
}
```

### 🚀 AI Enhancement Features

#### **Dynamic Intelligence**
- **Context-Aware**: Uses RAG to incorporate relevant knowledge during routing
- **Adaptive Learning**: Learns from successful patterns and user feedback
- **Multi-Modal Reasoning**: Combines keyword analysis, pattern matching, and LLM reasoning

#### **Quality Assurance**
- **Confidence Scoring**: Transparent confidence levels for decision transparency
- **Fallback System**: Rule-based routing if AI is unavailable
- **Error Recovery**: Graceful degradation with detailed logging

#### **Performance Optimization**
- **Rate Limiting**: 120 requests/minute protection
- **Async Processing**: Non-blocking AI operations
- **Caching**: Intelligent response caching for repeated queries

### 🛠️ Advanced Configuration

#### **Environment Variables**
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# AI Agent Settings
AI_AGENT_MODEL=gpt-4o-mini
AI_AGENT_TEMPERATURE=0.3
AI_AGENT_MAX_TOKENS=1000

# RAG Integration
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_CONTEXT_DOCS=3
```

#### **Customization**
To extend the AI orchestrator:

1. **Add New Agents**: Extend `AgentType` enum and update AI system prompt
2. **Customize Reasoning**: Modify the system prompt in `AIAgentRouter.SYSTEM_PROMPT`
3. **Enhance RAG**: Add domain-specific knowledge to improve routing accuracy
4. **Fine-tune Models**: Adjust temperature and token limits for different use cases

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

**JSON-RPC Input Format Issues**
```bash
# Ensure proper JSON format (no trailing commas, correct quotes)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/server.py

# For Windows PowerShell, use proper escaping
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/server.py

# Test with jq for validation (if available)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq . | python mcp/server.py
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
- Rebuild vector store: `rm -rf rag/store/ && python rag/ingest.py --paths knowledge/`

**AI Agent Routing Issues**
```bash
# Test AI agent functionality
python -c "from mcp.orchestrator import route_goal_async; import asyncio; result = asyncio.run(route_goal_async('test task')); print(result)"

# Check OpenAI API key
echo $OPENAI_API_KEY

# Test OpenAI connectivity
python -c "import openai; client = openai.OpenAI(); print('OpenAI connected')"
```

**AI Agent Returns Errors**
- Verify OpenAI API key is valid and has credits
- Check network connectivity to OpenAI services
- Ensure rate limits aren't exceeded (max 120 req/min)
- Try fallback routing: system automatically uses rule-based routing if AI fails

**RAG Context Not Available**
- Ensure knowledge base is populated: `python rag/ingest.py --paths knowledge/`
- Check ChromaDB storage: verify files exist in `rag/store/`
- Test RAG search: `python -c "from mcp.server import RAGServer; r = RAGServer(); print(r.search_knowledge('test'))"`

**High Token Usage**
- Monitor OpenAI API usage in your OpenAI dashboard
- Adjust AI_AGENT_MAX_TOKENS in .env (default: 1000)
- Use shorter task descriptions for routing
- Consider caching frequent routing decisions

**ChromaDB Schema Issues**
```bash
# If you see "no such column: collections.topic" errors
rm -rf rag/store/
python rag/ingest.py --paths knowledge/
```

### Docker-Specific Issues

**Container Won't Start**
```bash
# Check Docker is running
docker info

# Test basic image build
docker build -t test-build .

# Check container logs
docker run --rm mcp-rag:latest echo "Container works"
```

**Volume Mount Issues**
```bash
# Ensure correct paths for volume mounts
docker run --rm -v "$(pwd)/knowledge:/app/knowledge" mcp-rag:latest ls -la /app/knowledge/

# For Windows, use forward slashes in volume paths
docker run --rm -v "C:/path/to/project/knowledge:/app/knowledge" mcp-rag:latest ls -la /app/knowledge/
```

**Compose Issues**
```bash
# Clean up and rebuild
docker compose down
docker compose up --build

# Check service logs
docker compose logs mcp
```

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

