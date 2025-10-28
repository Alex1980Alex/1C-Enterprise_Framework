# Claude Safety Rules

## MCP Documentation Server Safety Rule

**CRITICAL: NEVER use `mcp__1c-framework-docs__reindex_docs` with `force: true`**

### Incident Details
- **Date**: 2025-10-20
- **Duration**: 2+ hours system hang
- **Cause**: Force reindexing created 26+ hanging Python processes
- **Resolution**: Required `taskkill /F /IM python.exe` to clear all processes

### Safe Practices
✅ **DO**: Use `mcp__1c-framework-docs__search_docs` for all documentation queries
✅ **DO**: Ask user permission before any reindexing operations
✅ **DO**: Warn about potential hang time if reindex is absolutely necessary

❌ **DON'T**: Use force reindexing without explicit user request
❌ **DON'T**: Assume reindexing is needed for better search results
❌ **DON'T**: Run reindexing operations in background

### Alternative Solutions
- Standard search works reliably for all documentation queries
- Manual reindexing by user when new docs are added
- Use existing search index which covers all framework documentation

### Emergency Recovery
If similar hang occurs:
```bash
powershell "taskkill /F /IM python.exe"
```

---
*This rule prevents system hangs and ensures reliable MCP operations.*