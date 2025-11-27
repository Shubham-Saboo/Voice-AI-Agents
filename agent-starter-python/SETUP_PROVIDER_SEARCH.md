# Provider Search System Setup Guide

This guide will help you set up the provider search system with SQLite and ChromaDB.

## Quick Start

### Step 1: Install Dependencies

```bash
cd agent-starter-python
uv sync
```

### Step 2: Run Data Migration

This will:
- Load providers from JSON file
- Create SQLite database (`providers.db`)
- Create ChromaDB vector database (`./chroma_db`)
- Generate embeddings using OpenAI API

```bash
uv run python src/migrate_data.py
```

**Note:** The migration will take a few minutes as it generates embeddings for all providers using OpenAI API. Make sure your `OPENAI_API_KEY` is set in `.env.local`.

### Step 3: Start the Agent

```bash
./START_AGENT.sh
```

Or manually:
```bash
uv run python src/agent.py dev
```

### Step 4: Test the Search

Start the webapp in another terminal:
```bash
cd ../vox-takehome-test
pnpm dev
```

Then test queries like:
- "Can you give me any 2 providers from Oklahoma City?"
- "Can you give me phone numbers of doctors in Milwaukee who do general surgery?"
- "Find me cardiologists in California"

## How It Works

### Architecture

1. **SQLite Database** (`providers.db`)
   - Stores all provider data with indexes on city, state, specialty
   - Fast exact match queries (5-20ms)

2. **ChromaDB Vector Database** (`./chroma_db`)
   - Stores embeddings for semantic search
   - Handles natural language queries (20-50ms)

3. **Hybrid Search**
   - Combines SQL filtering + vector search
   - Ranks results by relevance score
   - Returns top-k results

### Search Flow

```
User Query → Entity Extraction → SQL Filter → Vector Search → Combine & Rank → Results
```

## Configuration

### Environment Variables (.env.local)

```bash
# Database (SQLite by default)
SQLITE_DB_PATH=./providers.db

# Vector Database
CHROMA_DB_PATH=./chroma_db

# Provider Data
PROVIDER_JSON_PATH=/path/to/providerlist.json

# OpenAI (for embeddings)
OPENAI_API_KEY=your_key_here
```

### Using PostgreSQL (Optional)

If you want to use PostgreSQL instead of SQLite, set:

```bash
POSTGRES_URL=postgresql://user:password@localhost:5432/providers_db
```

Then re-run the migration script.

## Troubleshooting

### Migration fails with "No module named 'chromadb'"
- Run `uv sync` to install dependencies

### Migration fails with OpenAI API error
- Check that `OPENAI_API_KEY` is set correctly in `.env.local`
- Verify your API key has credits/quota

### Agent can't find providers
- Make sure migration completed successfully
- Check that `providers.db` exists in the project directory
- Verify `./chroma_db` directory exists

### Slow search performance
- First search may be slower (cold start)
- Subsequent searches should be faster (cached embeddings)
- For 1000 providers, expect 25-70ms latency

## Files Created

- `src/database.py` - SQLite/PostgreSQL database models
- `src/vector_db.py` - ChromaDB vector database client
- `src/search_service.py` - Hybrid search service
- `src/migrate_data.py` - Data migration script
- `src/agent.py` - Updated with search_providers tool

## Next Steps

After successful setup, you can:
1. Test various search queries
2. Optimize search parameters (limit, filters)
3. Add caching for common queries
4. Enhance entity extraction for better query parsing
5. Add UI components to display provider details (bonus feature)



