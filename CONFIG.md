# ⚙️ Configuration - Olcia AI Agent

## API Keys - Required

Olcia needs access to an AI model. Choose one provider and configure the API key.

### Option 1: Claude 3.5 Sonnet (Best Results) ⭐⭐⭐⭐⭐

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create account and generate API key
3. Add to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Advantages:**
- Best code understanding
- Great for complex architectural tasks
- Best Chain-of-Thought reasoning

### Option 2: OpenAI GPT-4o (Good Results) ⭐⭐⭐⭐

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create API key
3. Add to `.env`:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_AGENT_MODEL=gpt-4o
```

**Advantages:**
- Great quality-price balance
- Good for most programming tasks

### Option 3: OpenAI GPT-4o-mini (Cheap) ⭐⭐⭐

1. Use the same API key as above
2. Add to `.env`:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_AGENT_MODEL=gpt-4o-mini
```

**Advantages:**
- Cheapest option
- Good for simple tasks

## 🔧 Advanced Configuration (Optional)

You can customize the AI agent's behavior through additional settings in `.env`:

```env
# AI response temperature (0.1 = more predictable, 0.7 = more creative)
AI_AGENT_TEMPERATURE=0.3

# Maximum tokens per response
AI_AGENT_MAX_TOKENS=1000

# Logging verbosity level
LOG_LEVEL=INFO

# Similarity threshold for RAG search (0.0-1.0)
RAG_SIMILARITY_THRESHOLD=0.7

# Maximum documents to retrieve from RAG
RAG_MAX_CONTEXT_DOCS=3

# Embedding model (don't change without reason)
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## 🧪 Testing Configuration

After configuring API key, test the connection:

### Test 1: Import modules
```bash
python -c "import mcp.server; print('✅ MCP Server OK')"
```

### Test 2: API Check
```bash
python -c "from mcp.orchestrator import route_goal; print(route_goal('test task'))"
```

### Test 3: Cursor IDE
Open project in Cursor and check if `@olcia-ai-agent` is available in chat.

## 🚨 Troubleshooting

### Problem: "MCP server not found" in Cursor
- Check if `.cursor/mcp.json` exists
- Restart Cursor IDE
- Make sure Python is in PATH

### Problem: "API key invalid"
- Check if API key is copied correctly
- Make sure there are no extra spaces
- Verify account balance with API provider

### Problem: "No response from AI"
- Check internet connection
- Verify API limits (rate limits)
- Try switching to cheaper model (GPT-4o-mini)

### Problem: "RAG search not working"
- Check if `rag/store/` folder exists and contains files
- Make sure vector database wasn't deleted

## 💡 Tips

- **Start with Claude** - gives best results for programming
- **Use GPT-4o-mini** for simple tasks to save costs
- **Monitor API usage** in provider dashboards
- **Log experiences** - AI will learn from your feedback

## 🔄 Updates

When you add new documents to `knowledge/`:
```bash
python rag/ingest.py --paths knowledge/
```

This will rebuild RAG indexes with new knowledge.

## 📞 Help

If you still have problems:
1. Check Cursor logs (Developer Tools)
2. Verify all configuration files
3. Try restarting Cursor
4. Check repo issues (if public)
