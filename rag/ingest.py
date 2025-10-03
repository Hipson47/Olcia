#!/usr/bin/env python3
"""
RAG Ingestion System for Local ChromaDB
Windows-first implementation with token-based chunking and file type support.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

try:
    import chromadb
    import fitz  # PyMuPDF
    import tiktoken
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    print("Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


class TextChunker:
    """Token-based text chunker with configurable overlap."""

    def __init__(self, chunk_size: int = 350, overlap_percent: float = 0.2, encoding_model: str = "cl100k_base"):
        """
        Initialize text chunker.

        Args:
            chunk_size: Target chunk size in tokens
            overlap_percent: Overlap between chunks as percentage of chunk_size
            encoding_model: Tiktoken encoding model for token counting
        """
        self.chunk_size = chunk_size
        self.overlap_percent = overlap_percent
        self.overlap_size = int(chunk_size * overlap_percent)

        try:
            self.encoding = tiktoken.get_encoding(encoding_model)
        except KeyError:
            # Fallback to a known encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str) -> list[str]:
        """
        Split text into chunks with token-based sizing and overlap.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text.strip():
            return []

        # If text is short, return as single chunk
        total_tokens = self.count_tokens(text)
        if total_tokens <= self.chunk_size:
            return [text]

        # Split into sentences/paragraphs for better chunk boundaries
        # Simple sentence splitting (can be enhanced)
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
        if not sentences:
            # Fallback: split by words if no sentences found
            words = text.split()
            sentences = [' '.join(words[i:i+50]) for i in range(0, len(words), 50)]

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence + ". ")

            # If adding this sentence would exceed chunk size
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + sentence + ". "
                current_tokens = self.count_tokens(current_chunk)
            else:
                current_chunk += sentence + ". "
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """Extract overlap text from the end of a chunk."""
        if not text:
            return ""

        words = text.split()
        if len(words) <= self.overlap_size:
            return text

        # Take approximately overlap_size tokens worth of text from the end
        overlap_text = ""
        token_count = 0

        for word in reversed(words):
            word_tokens = self.count_tokens(word + " ")
            if token_count + word_tokens > self.overlap_size:
                break
            overlap_text = word + " " + overlap_text
            token_count += word_tokens

        return overlap_text.strip() + " "


class FileLoader:
    """Load content from different file types."""

    def __init__(self, max_file_size_mb: int = 50, text_encoding: str = "utf-8"):
        """
        Initialize file loader.

        Args:
            max_file_size_mb: Maximum file size to load
            text_encoding: Text encoding for text files
        """
        self.max_file_size_mb = max_file_size_mb
        self.text_encoding = text_encoding

    def load_file(self, file_path: str | Path) -> str:
        """
        Load content from file based on extension.

        Args:
            file_path: Path to file to load

        Returns:
            File content as string

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file doesn't exist
        """
        # Handle both Path objects and strings
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB")

        suffix = file_path.suffix.lower()

        if suffix == ".md":
            return self._load_markdown(file_path)
        elif suffix == ".json":
            return self._load_json(file_path)
        elif suffix == ".pdf":
            return self._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _load_markdown(self, file_path: Path) -> str:
        """Load markdown file."""
        with open(file_path, encoding=self.text_encoding) as f:
            return f.read()

    def _load_json(self, file_path: Path) -> str:
        """Load JSON file and convert to readable text."""
        with open(file_path, encoding=self.text_encoding) as f:
            data = json.load(f)

        # Convert JSON to readable text representation
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _load_pdf(self, file_path: Path) -> str:
        """Load PDF file using PyMuPDF."""
        text = ""
        with fitz.open(str(file_path)) as doc:
            for page in doc:
                text += page.get_text() + "\n"

        return text.strip()


class RAGIngestor:
    """Main RAG ingestion orchestrator with ChromaDB persistence."""

    def __init__(self, config_path: Path | None = None, persist_directory: str | None = None):
        """
        Initialize RAG ingestor.

        Args:
            config_path: Path to config YAML file
            persist_directory: Override persist directory
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"

        yaml_loader = YAML()
        with open(config_path, encoding='utf-8') as f:
            self.config = yaml_loader.load(f)

        # Override persist directory if specified
        if persist_directory:
            self.config['ingestion']['chroma']['persist_directory'] = persist_directory

        # Initialize components
        self._setup_logging()
        self._init_chunker()
        self._init_file_loader()
        self._init_embedding_model()
        self._init_chroma_client()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger = logging.getLogger(__name__)

    def _init_chunker(self) -> None:
        """Initialize text chunker."""
        chunk_config = self.config['ingestion']['chunking']
        self.chunker = TextChunker(
            chunk_size=chunk_config['chunk_size'],
            overlap_percent=chunk_config['overlap_percent'],
            encoding_model=chunk_config['encoding_model']
        )

    def _init_file_loader(self) -> None:
        """Initialize file loader."""
        process_config = self.config['ingestion']['processing']
        self.file_loader = FileLoader(
            max_file_size_mb=process_config['max_file_size_mb'],
            text_encoding=process_config['text_encoding']
        )

    def _init_embedding_model(self) -> None:
        """Initialize sentence transformer model."""
        embed_config = self.config['ingestion']['embedding']
        self.logger.info(f"Loading embedding model: {embed_config['model_name']}")
        self.embedding_model = SentenceTransformer(
            embed_config['model_name'],
            device=embed_config['device']
        )

    def _init_chroma_client(self) -> None:
        """Initialize ChromaDB client."""
        chroma_config = self.config['ingestion']['chroma']
        persist_dir = Path(__file__).parent / chroma_config['persist_directory']
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initializing ChromaDB at: {persist_dir}")
        self.chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name=chroma_config['collection_name']
        )

    def ingest_file(self, file_path: Path) -> dict[str, Any]:
        """
        Ingest a single file into the RAG system.

        Args:
            file_path: Path to file to ingest

        Returns:
            Ingestion result dictionary
        """
        result = {
            "file_path": str(file_path),
            "status": "pending",
            "chunks_count": 0,
            "timestamp": time.time()
        }

        try:
            # Check if file type is supported
            if file_path.suffix.lower() not in self.config['ingestion']['file_types']:
                result.update({
                    "status": "skipped",
                    "reason": f"Unsupported file type: {file_path.suffix}"
                })
                return result

            # Load file content
            self.logger.info(f"Loading file: {file_path}")
            content = self.file_loader.load_file(file_path)

            if not content.strip():
                result.update({
                    "status": "skipped",
                    "reason": "Empty file"
                })
                return result

            # Chunk the content
            self.logger.info(f"Chunking content: {len(content)} chars")
            chunks = self.chunker.chunk_text(content)
            result["chunks_count"] = len(chunks)

            if not chunks:
                result.update({
                    "status": "skipped",
                    "reason": "No chunks generated"
                })
                return result

            # Generate embeddings
            self.logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embedding_model.encode(chunks, batch_size=self.config['ingestion']['embedding']['batch_size'])

            # Prepare metadata
            base_metadata = {
                "source_file": str(file_path),
                "file_type": file_path.suffix.lower(),
                "ingestion_timestamp": str(result["timestamp"])
            }

            # Add chunks to ChromaDB
            self.logger.info(f"Adding {len(chunks)} chunks to ChromaDB")
            ids = []
            metadatas = []
            documents = []

            for i, (chunk, _embedding) in enumerate(zip(chunks, embeddings, strict=False)):
                chunk_id = f"{file_path.stem}_chunk_{i}"
                metadata = base_metadata.copy()
                metadata.update({
                    "chunk_index": str(i),
                    "total_chunks": str(len(chunks))
                })

                ids.append(chunk_id)
                metadatas.append(metadata)
                documents.append(chunk)

            # Handle both numpy arrays and plain Python lists
            if hasattr(embeddings, 'tolist'):
                embedding_list = embeddings.tolist()
            else:
                embedding_list = embeddings

            self.collection.add(
                embeddings=embedding_list,
                documents=documents,
                metadatas=metadatas,  # type: ignore[arg-type]
                ids=ids
            )

            result["status"] = "success"
            self.logger.info(f"Successfully ingested {len(chunks)} chunks from {file_path}")

        except Exception as e:
            self.logger.error(f"Error ingesting {file_path}: {str(e)}")
            result.update({
                "status": "error",
                "error": str(e)
            })

        return result

    def ingest_directory(self, directory_path: Path) -> list[dict[str, Any]]:
        """
        Ingest all supported files in a directory.

        Args:
            directory_path: Path to directory to ingest

        Returns:
            List of ingestion results
        """
        if not directory_path.exists() or not directory_path.is_dir():
            return [{"status": "error", "error": f"Directory not found: {directory_path}"}]

        results = []
        file_types = set(self.config['ingestion']['file_types'])
        skip_patterns = set(self.config['ingestion']['processing']['skip_patterns'])

        # Find all files recursively
        for file_path in directory_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip hidden files
            if self.config['ingestion']['processing']['skip_hidden'] and file_path.name.startswith('.'):
                continue

            # Skip files matching patterns
            if any(file_path.match(pattern) for pattern in skip_patterns):
                continue

            # Check file type
            if file_path.suffix.lower() in file_types:
                result = self.ingest_file(file_path)
                results.append(result)

        return results

    def _normalize_path(self, path: str) -> Path:
        """Normalize path for cross-platform compatibility."""
        return Path(path).resolve()


def main() -> None:
    """Command line interface for RAG ingestion."""
    parser = argparse.ArgumentParser(description="RAG Ingestion System")
    parser.add_argument(
        "--paths", nargs="+", required=True,
        help="Paths to files or directories to ingest"
    )
    parser.add_argument(
        "--config", type=Path,
        help="Path to config YAML file"
    )
    parser.add_argument(
        "--persist-dir", type=str,
        help="Override ChromaDB persist directory"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        # Initialize ingestor
        ingestor = RAGIngestor(config_path=args.config, persist_directory=args.persist_dir)

        all_results = []

        # Process each path
        for path_str in args.paths:
            path = Path(path_str)

            if path.is_file():
                result = ingestor.ingest_file(path)
                all_results.append(result)
            elif path.is_dir():
                results = ingestor.ingest_directory(path)
                all_results.extend(results)
            else:
                all_results.append({
                    "status": "error",
                    "error": f"Path not found: {path}",
                    "path": str(path)
                })

        # Print summary
        successful = sum(1 for r in all_results if r.get("status") == "success")
        errors = sum(1 for r in all_results if r.get("status") == "error")
        skipped = sum(1 for r in all_results if r.get("status") == "skipped")

        print("\nIngestion Summary:")
        print(f"  Successful: {successful}")
        print(f"  Errors: {errors}")
        print(f"  Skipped: {skipped}")

        if errors > 0:
            print("\nErrors:")
            for result in all_results:
                if result.get("status") == "error":
                    print(f"  {result.get('file_path', 'Unknown')}: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
