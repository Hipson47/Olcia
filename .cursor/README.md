# Olcia - Portable MCP+RAG Agent for Cursor

Intelligent Cursor agent with RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol) for any codebase.

## 📋 Prerequisites

- **Python**: 3.11+ (tested with 3.13.5)
- **Git**: For repository management
- **API Keys**: OpenAI and/or Anthropic API access
- **Cursor Editor**: Latest version with MCP support

## 🚀 Quick Setup - Copy into Any Repo

### 1. Copy Olcia into Your Project
```bash
# From your project root directory:
git clone https://github.com/Hipson47/Olcia.git temp-olcia
cp -r temp-olcia/.cursor ./
rm -rf temp-olcia

# Or download and extract manually
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Bootstrap Dependencies
```powershell
# Windows PowerShell (recommended)
.\.cursor\scripts\bootstrap.ps1

# Or manually:
pip install python-dotenv chromadb sentence-transformers
```

### 4. Launch Cursor
Open your project in Cursor - the MCP server starts automatically!

## 🔄 Automatic Start Behavior

When you open a project with `.cursor/` directory in Cursor:

1. **MCP Detection**: Cursor finds `.cursor/mcp.json`
2. **Server Launch**: Starts `.cursor/mcp/server.py` with Python
3. **Environment Loading**: Loads `.env` from project root
4. **RAG Initialization**: Indexes `.cursor/knowledge/` files
5. **Tool Registration**: Makes all MCP tools available via `@cursor-agent`

## 🛠️ Bootstrap Commands

### Automated Bootstrap (Recommended)
```powershell
# Windows - creates venv and installs dependencies
.\.cursor\scripts\bootstrap.ps1
```

### Manual Bootstrap
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install python-dotenv chromadb sentence-transformers

# Verify installation
python -c "import dotenv, chromadb, sentence_transformers; print('✅ Ready')"
```

## 🎯 Using the Planning Pipeline

### Core Commands

Use these prompts in Cursor to access the intelligent planning system:

#### `/plan` - Strategic Planning
```
Generate comprehensive implementation plans using Tree-of-Thought + Graph-of-Thought reasoning.

Usage: Describe your task, get a ≤10-step micro-plan with test contracts.
Example: "Implement user authentication for my web app"
```

#### `/verify` - Quality Assurance
```
Critique plans with CISC consensus voting.

Usage: Review plans for quality, safety, and testability. Drops <0.6 rated steps.
Example: "Verify this authentication plan meets security standards"
```

#### `/apply` - Safe Execution
```
Apply minimal unified diffs within declared scope.

Usage: Implement verified plans with surgical precision. Satisfies test contracts.
Example: "Apply the authentication implementation safely"
```

#### `/tdd` - Test-Driven Development
```
Red-Green-Refactor TDD cycle.

Usage: Write failing tests, implement minimal code, refactor safely.
Example: "Create TDD tests for user login functionality"
```

#### `/rag` - Knowledge Retrieval
```
Fetch 5-10 snippets from project knowledge and external docs.

Usage: Ground reasoning in retrieved facts, cite sources, prune inconsistencies.
Example: "Research authentication best practices for web apps"
```

### Pipeline Workflow

```
1. /rag     → Gather context and facts
2. /plan    → Generate strategic plan
3. /verify  → Quality check and consensus
4. /apply   → Safe implementation
5. /tdd     → Test-driven validation
```

## 🧠 MoE (Mixture of Experts) Overview

Olcia uses intelligent expert orchestration:

### Expert Pool
- **Planner**: Strategic decomposition and acceptance criteria
- **Coder**: Safe editing with minimal diffs
- **Tester**: TDD loops and assertion validation
- **Refactor**: Code quality improvements
- **Security**: Secrets scanning and vulnerability fixes
- **RAG Researcher**: Evidence-based information retrieval

### Routing Intelligence
- **Feature Analysis**: File types, keywords, RAG requirements, safety risks
- **Rule-Based Selection**: Conditional expert matching
- **Confidence Weighting**: Consensus voting with early stopping
- **Metrics Logging**: Reasoning KPIs per request

### Example MoE Decision
```
Task: "Add user auth to Python web app"
Analysis: file_ext=py, goal_keywords=auth, requires_rag=false
Routing: [coder, tester] (85% confidence)
Execution: Safe implementation + comprehensive testing
```

## 🔧 Troubleshooting

### MCP Server Won't Start (Red Status Icon)

**Symptoms**: Cursor shows red MCP status, tools unavailable

**Solutions**:
```bash
# 1. Check Python availability
python --version

# 2. Verify dependencies
python -c "import chromadb, dotenv, sentence_transformers"

# 3. Check environment file
ls -la .env

# 4. Restart Cursor completely
# 5. Check Cursor console logs for error messages
```

### API Key Errors
```
Error: OPENAI_API_KEY not found
```

**Fix**:
```bash
# Ensure .env exists in project root (not .cursor/)
cp .env.example .env
# Edit .env with your actual API keys
```

### Import Errors
```
ModuleNotFoundError: No module named 'chromadb'
```

**Fix**:
```powershell
# Re-run bootstrap
.\.cursor\scripts\bootstrap.ps1

# Or manual install
pip install python-dotenv chromadb sentence-transformers
```

### RAG Not Working
```
No snippets found for query
```

**Fix**:
```bash
# Add knowledge files
echo "Your project documentation here" > .cursor/knowledge/project.md

# Or add existing docs
cp docs/*.md .cursor/knowledge/
```

### Slow Performance
**Optimizations**:
```bash
# Reduce RAG context
# Use specific file references in queries
# Limit search results: k=3 instead of k=10
```

### Windows-Specific Issues
```powershell
# Use PowerShell for bootstrap
.\.cursor\scripts\bootstrap.ps1

# Check execution policy
Get-ExecutionPolicy

# If needed: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📁 Project Structure

```
.cursor/
├── mcp/
│   ├── server.py          # Main MCP server with MoE routing
│   ├── moe.py            # Mixture of Experts implementation
│   └── [other modules]
├── knowledge/            # RAG knowledge base (PDF, MD, TXT)
├── rules/
│   ├── moe.yml          # Expert routing configuration
│   ├── reasoning.yml    # ToT+GoT+CISC settings
│   └── agent.mdc        # Agent behavior rules
├── prompts/
│   ├── plan.md          # ToT+GoT planning
│   ├── verify.md        # CISC verification
│   ├── apply.md         # Safe edit execution
│   ├── tdd.md           # Test-driven development
│   ├── rag.md           # Knowledge retrieval
│   └── experts/         # Specialized expert prompts
├── scripts/
│   └── bootstrap.ps1    # Windows setup script
├── mcp.json            # MCP server configuration
├── pyproject.toml      # Python dependencies
└── README.md           # This documentation
```

## 🔐 Security Notes

- **Never commit** `.env` files with real API keys
- **Use environment variables** for sensitive configuration
- **Regular key rotation** recommended
- **Monitor API usage** to avoid unexpected charges

## 📖 Advanced Usage

### Custom Knowledge Ingestion
```python
# Add project-specific documentation
from mcp.server import RAGServer
rag = RAGServer()
rag.add_knowledge("Your docs here", {"source_file": "custom.md"})
```

### Expert Customization
Edit `.cursor/rules/moe.yml` to modify expert routing rules and add custom experts.

### Metrics Monitoring
Check stderr output for reasoning KPIs:
```
METRICS: {"explored_nodes": 7, "merged_nodes": 2, "vote_distribution": {...}, "confidence": 0.82}
```

## 🤝 Contributing

1. **Copy .cursor/** into your project
2. **Customize** prompts and rules for your needs
3. **Add knowledge** files to `.cursor/knowledge/`
4. **Share improvements** back to the community

## 📝 License

MIT License - see LICENSE file

## 🆘 Getting Help

1. **Check this README** for common solutions
2. **Verify prerequisites** (Python 3.11+, API keys)
3. **Run bootstrap** to ensure dependencies
4. **Check Cursor logs** for detailed error messages
5. **Create an issue** with full error output and environment details

