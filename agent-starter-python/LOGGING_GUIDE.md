# Logging Guide

This guide explains the logging system for debugging provider search functionality.

## Log Levels

The system uses structured logging with emojis for easy identification:

- 📝 **User Search Request** - Logs the original user query and extracted parameters
- 🔍 **Search Execution** - Logs search parameters and execution details
- ✅ **Search Results** - Logs number of results found from each search method
- 📊 **Search Summary** - Logs final combined results
- 💬 **Agent Response** - Logs the response sent to the user
- ⚠️ **Warnings** - Logs when no results are found
- ❌ **Errors** - Logs errors with full stack traces

## What Gets Logged

### 1. User Query Logging
When a user asks a question, the system logs:
- Original user query text
- Extracted city, state, specialty parameters
- Search limit

Example:
```
📝 User search request: {
  "user_query": "find pediatricians in Tennessee",
  "extracted_city": null,
  "extracted_state": "Tennessee",
  "extracted_specialty": "pediatrics",
  "limit": 5
}
```

### 2. Search Execution Logging
The search service logs:
- Search parameters (query, filters, limit)
- SQL search results count
- Vector search results count
- Combined results count

Example:
```
🔍 Starting provider search: {
  "query": "pediatricians",
  "city": null,
  "state": "Tennessee",
  "specialty": "pediatrics",
  "limit": 5
}
✅ SQL search returned 3 results
✅ Vector search returned 5 results
🎯 Final combined results: 5 providers
```

### 3. Results Logging
For successful searches:
- Number of providers found
- Summary of top results (name, specialty, location)

Example:
```
📊 Search completed: found 5 providers
Results summary: [
  {"name": "Dr. John Smith", "specialty": "Pediatrics", "location": "Nashville, TN"},
  ...
]
```

### 4. No Results Logging
When no results are found:
- Warning log with search parameters
- Human-friendly error message sent to user

Example:
```
⚠️ No results found for query: pediatricians, city=None, state=Tennessee, specialty=pediatrics
```

### 5. Error Logging
When errors occur:
- Full error message
- Stack trace
- Search parameters that caused the error

Example:
```
❌ Error searching providers: ValueError: ...
Error details - query=pediatricians, city=None, state=Tennessee, specialty=pediatrics
```

### 6. Agent Response Logging
Before sending response to user:
- Response length
- Response preview (first 200 characters)

Example:
```
💬 Agent response generated: 450 characters
Response preview: I found 5 providers: 1. Dr. John Smith...
```

## Viewing Logs

### During Development
Logs are printed to console with timestamps. Look for:
- Search-related logs (📝, 🔍, ✅, 📊)
- Error logs (❌)
- Warning logs (⚠️)

### In Production
Logs follow standard Python logging format and can be:
- Redirected to files
- Sent to logging services (e.g., Datadog, CloudWatch)
- Filtered by log level

## Debugging Tips

1. **No Results Found**
   - Check ⚠️ warning logs for search parameters
   - Verify data was migrated correctly
   - Check if filters are too restrictive

2. **Search Errors**
   - Check ❌ error logs for full stack trace
   - Verify database connection
   - Check ChromaDB filter syntax

3. **Slow Performance**
   - Check 🔍 search execution logs for timing
   - Monitor SQL vs vector search counts
   - Check if embeddings are being generated on-the-fly

4. **Wrong Results**
   - Check 📊 search summary logs
   - Verify extracted parameters match user intent
   - Check SQL and vector search results separately

## Logging Configuration

To change log levels, modify the logging configuration in `agent.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more detail
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

Available log levels:
- `DEBUG` - Very detailed logs (includes all debug statements)
- `INFO` - Standard operational logs (default)
- `WARNING` - Warnings only
- `ERROR` - Errors only



