# MCP+RAG Server Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libyaml-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./
# Ensure lock file is up to date
RUN poetry lock --check || poetry lock --no-update

# Install Python dependencies (only main dependencies, no dev)
RUN poetry config virtualenvs.create false \
    && echo "Installing Python dependencies..." \
    && poetry install --only main --no-root --no-interaction --no-ansi \
    && echo "Dependencies installed. Verifying key packages..." \
    && python -c "
try:
    from ruamel.yaml import YAML
    print('✓ ruamel.yaml successfully installed')
except ImportError as e:
    print('✗ ruamel.yaml failed:', e)
    exit(1)

try:
    import chromadb
    print('✓ chromadb available')
except ImportError as e:
    print('✗ chromadb failed:', e)
    exit(1)

print('All key dependencies verified!')
"

# Copy application code
COPY mcp/ ./mcp/
COPY rag/ ./rag/

# Create necessary directories
RUN mkdir -p /app/knowledge /app/rag/store /app/memory

# Declare volumes for persistent data
VOLUME ["/app/knowledge", "/app/rag/store"]

# Set entrypoint
ENTRYPOINT ["python", "mcp/server.py"]
