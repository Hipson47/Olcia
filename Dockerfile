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

# Install Python dependencies (only main dependencies, no dev)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

# Copy application code
COPY mcp/ ./mcp/
COPY rag/ ./rag/
COPY memory/ ./memory/

# Create necessary directories
RUN mkdir -p /app/knowledge /app/rag/store /app/memory

# Declare volumes for persistent data
VOLUME ["/app/knowledge", "/app/rag/store"]

# Set entrypoint
ENTRYPOINT ["python", "mcp/server.py"]
