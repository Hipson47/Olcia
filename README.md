# 🤖 Olcia AI Agent

**Ready-to-use AI Agent repository for Cursor IDE**

Intelligent programming assistant with RAG knowledge base that helps build applications through automatic task recognition and best practice delivery.

## ⚡ Quick Start (2 minutes)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd olcia-ai-agent
```

### 2. Configure API Key
```bash
# Copy configuration template
cp .env.example .env

# Edit .env and add one of these lines:
# For Claude 3.5 Sonnet (recommended):
# ANTHROPIC_API_KEY=sk-ant-api03-...

# For OpenAI GPT-4o:
# OPENAI_API_KEY=sk-...
# AI_AGENT_MODEL=gpt-4o
```

### 3. Open in Cursor
```
File → Open Folder → select olcia-ai-agent directory
```

### 4. Use AI Agent
```
@olcia-ai-agent route: "Implement REST API for user management"
@olcia-ai-agent search: "authentication best practices"
@olcia-ai-agent log: "API implementation completed successfully"
```

## 🎯 What can Olcia do?

### 🤖 Intelligent Task Routing
Automatically recognizes task type and selects appropriate AI specialist:
- **General** - Architecture, API, backend
- **Tests** - TDD, testing, QA
- **Database** - Schemas, migrations, optimization

### 🔍 Knowledge Search (RAG)
- Over 20 documents with best practices
- Semantic search with embeddings
- Context-aware responses

### 📚 Learning from Experience
- Memory of successful and failed approaches
- Learning from feedback
- Continuously improving response quality

## 🛠️ Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `@olcia-ai-agent route` | AI task routing | `@olcia-ai-agent route: "Implement JWT auth"` |
| `@olcia-ai-agent search` | Knowledge search | `@olcia-ai-agent search: "OAuth2 patterns"` |
| `@olcia-ai-agent log` | Experience logging | `@olcia-ai-agent log: "JWT impl successful"` |
| `@olcia-ai-agent add_memory` | Add memories | `@olcia-ai-agent add_memory: "lesson learned"` |
| `@olcia-ai-agent add_knowledge` | Add knowledge | `@olcia-ai-agent add_knowledge: "new doc"` |

## 📋 Usage Examples

### API Development
```
@olcia-ai-agent route: "Implement JWT authentication for REST API with refresh tokens"
```

### Testing
```
@olcia-ai-agent route: "Create comprehensive test suite for user registration with TDD approach"
```

### Database Design
```
@olcia-ai-agent route: "Design PostgreSQL schema for social media analytics platform"
```

### Knowledge Search
```
@olcia-ai-agent search: "API security best practices"
@olcia-ai-agent search: "microservices architecture patterns"
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cursor IDE    │───▶│   MCP Server    │───▶│  AI Agent       │
│   (User Input)  │    │   (Python)      │    │  (Claude/GPT)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  RAG System     │    │  Knowledge Base │    │   Memory        │
│  (ChromaDB)     │    │  (Embeddings)   │    │   (Learning)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ⚙️ Configuration

All settings in `.env` file:

```env
# ==========================================
# AI MODEL CONFIGURATION (Choose ONE)
# ==========================================

# Option 1: Claude 3.5 Sonnet (RECOMMENDED)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Option 2: OpenAI GPT-4o
OPENAI_API_KEY=your_openai_api_key_here
AI_AGENT_MODEL=gpt-4o

# Option 3: OpenAI GPT-4o-mini (Cost-effective)
# OPENAI_API_KEY=your_openai_api_key_here
# AI_AGENT_MODEL=gpt-4o-mini

# ==========================================
# OPTIONAL SETTINGS
# ==========================================

# Agent temperature (0.1-0.7)
AI_AGENT_TEMPERATURE=0.3

# Max tokens per request
AI_AGENT_MAX_TOKENS=1000

# Logging level
LOG_LEVEL=INFO

# RAG similarity threshold
RAG_SIMILARITY_THRESHOLD=0.7
```

## 📊 Status and Capabilities

- ✅ **MCP Server**: Fully functional
- ✅ **RAG System**: ChromaDB with ready embeddings
- ✅ **Knowledge Base**: 20+ documents with best practices
- ✅ **AI Models**: Claude 3.5 Sonnet / GPT-4o / GPT-4o-mini
- ✅ **Memory**: Experience learning system
- ✅ **Cursor IDE**: Full MCP integration

## 🚀 What's Next?

1. **Experiment** with different task types
2. **Add knowledge** - AI learns from your documents
3. **Log experiences** - improves response quality
4. **Share** - show others how to use Olcia!

## 📞 Support

- **Documentation**: All README files in repo
- **Configuration**: Check `.env.example`
- **Issues**: Verify API keys and Cursor connection

---

**Powered by Cursor IDE + MCP + ChromaDB + AI Agents**

*Made with ❤️ for developers who want AI assistance in their workflow*
