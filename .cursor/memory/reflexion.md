# Lessons Learned & Reflection Notes

## Recent Insights

### 1. Error Handling in Async Contexts
**Date**: 2025-10-02
**Lesson**: When implementing async MCP tools, always wrap database operations in try-catch blocks and provide meaningful error messages. Forgetting to handle connection timeouts can cause silent failures that are hard to debug.

**Context**: During RAG ingestion implementation, ChromaDB operations occasionally timed out but weren't properly logged, making troubleshooting difficult.

**Action**: Added comprehensive error handling with detailed logging for all async operations.

### 2. Path Handling Across Platforms
**Date**: 2025-10-02
**Lesson**: Always use `pathlib.Path` objects instead of string concatenation for file paths, especially when dealing with Windows/Unix compatibility. The `resolve()` method ensures proper path normalization.

**Context**: File ingestion failed on some Windows paths due to inconsistent path separators and relative path handling.

**Action**: Standardized all file operations to use `pathlib.Path` with proper resolution.

### 3. Test Data Management
**Date**: 2025-10-02
**Lesson**: When testing file system operations, use `tempfile` with proper cleanup to avoid test interference. Temporary directories should be created fresh for each test and cleaned up automatically.

**Context**: Multiple tests were interfering with each other due to shared temporary files and directories.

**Action**: Implemented proper temporary directory management with automatic cleanup in test tearDown methods.

---

## Patterns to Remember

- **Append-only logging**: Use JSONL format for reliable, append-only error logs
- **Type hints**: Always add type hints to function signatures for better IDE support
- **Error propagation**: Let errors bubble up to the MCP layer for consistent error formatting
- **Path normalization**: Use pathlib for all file operations across platforms

### 4. E2E System Integration Testing
**Date**: 2025-10-02
**Lesson**: End-to-end testing of the complete MCP+RAG system revealed the importance of testing the full pipeline from ingestion to querying to orchestration. Each component works individually but integration points can have subtle issues.

**Context**: During E2E demo, discovered that ChromaDB initialization happens lazily in the MCP server, which could cause timeouts for the first query after server restart.

**Action**: Consider pre-initializing heavy components or implementing connection pooling for better user experience.

## Future Considerations

- Consider adding log rotation for mistakes.jsonl when it grows too large
- Implement error categorization and severity levels
- Add reflection prompts for regular review of logged errors
- Consider pre-initialization of ML models to reduce first-query latency
