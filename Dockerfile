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
    && echo "Verifying PyYAML installation..." \
    && python -c "import yaml; print('PyYAML successfully installed')" \
    && echo "Verifying other key packages..." \
    && python -c "import chromadb; print('chromadb available')"

# Copy application code
COPY mcp/ ./mcp/
COPY rag/ ./rag/

# Create necessary directories
RUN mkdir -p /app/knowledge /app/rag/store /app/memory

# Declare volumes for persistent data
VOLUME ["/app/knowledge", "/app/rag/store"]

# Set entrypoint
ENTRYPOINT ["python", "mcp/server.py"]
