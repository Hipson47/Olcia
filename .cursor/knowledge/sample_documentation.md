# RAG System Documentation

## Overview

The Retrieval-Augmented Generation (RAG) system provides intelligent knowledge management and question answering capabilities. This system combines local document storage with vector embeddings to enable semantic search and context-aware responses.

## Architecture

### Components

1. **Document Ingestion Pipeline**
   - Supports multiple file formats (Markdown, PDF, JSON)
   - Token-based text chunking with configurable overlap
   - Local embedding generation using Sentence Transformers
   - Persistent storage in ChromaDB vector database

2. **Query Processing**
   - Semantic similarity search across document chunks
   - Context-aware response generation
   - Integration with MCP (Model Context Protocol) servers

3. **File Watching System**
   - Automatic re-ingestion on document changes
   - Debounced updates to prevent excessive processing
   - Windows-native PowerShell implementation

## Configuration

The system is configured via `rag/config.yaml` with the following key settings:

- **Chunking**: 350 tokens per chunk with 20% overlap
- **Embedding**: all-MiniLM-L6-v2 model running on CPU
- **File Types**: .md, .pdf, .json support
- **Storage**: Local ChromaDB persistence

## Usage Examples

### Basic Ingestion

```bash
python rag/ingest.py --paths knowledge/
```

### Auto-Watching

```powershell
.\scripts\auto_ingest.ps1
```

### Query Interface

The system integrates with Cursor via MCP protocol, providing tools for:
- Knowledge base searches
- Context retrieval
- Memory management

## Development Workflow

Follow the structured approach:
1. **Plan** - Design changes with task breakdown
2. **Code** - Implement following established patterns
3. **Test** - Validate with comprehensive test suite
4. **Review** - Ensure minimal diffs and proper documentation

## Performance Considerations

- Local embeddings provide privacy and speed
- Token-based chunking ensures consistent processing
- Debounced file watching prevents resource waste
- ChromaDB enables efficient vector similarity search

## Security

- No external API dependencies for core functionality
- Local storage prevents data leakage
- Configurable file type restrictions
- Input validation and error handling
