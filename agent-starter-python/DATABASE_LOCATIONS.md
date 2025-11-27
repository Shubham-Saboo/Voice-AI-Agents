# Database Locations and Access

## Database Storage Locations

### 1. SQLite Database (providers.db)

**Location:** `/Users/shubhamsaboo/Voxology/agent-starter-python/providers.db`

**Configuration:**
- Default path: `./providers.db` (relative to `agent-starter-python` directory)
- Can be customized via `SQLITE_DB_PATH` in `.env.local`
- Current size: ~68KB
- Contains: 100 providers (migrated from JSON)

**How Agent Accesses It:**
- The agent imports `database.py` which creates a global `db` instance
- SQLAlchemy handles the connection automatically
- Path is resolved relative to where the agent script runs from
- No credentials needed (SQLite is file-based)

**Code Reference:**
```python
# In src/database.py
db_path = os.getenv("SQLITE_DB_PATH", "./providers.db")
db_url = f"sqlite:///{db_path}"
```

### 2. ChromaDB Vector Database

**Location:** `/Users/shubhamsaboo/Voxology/agent-starter-python/chroma_db/`

**Configuration:**
- Default path: `./chroma_db` (relative to `agent-starter-python` directory)
- Can be customized via `CHROMA_DB_PATH` in `.env.local`
- Contains: Vector embeddings for all 100 providers
- Storage: Local directory with `chroma.sqlite3` file (~1MB)

**How Agent Accesses It:**
- The agent imports `vector_db.py` which creates a global `vector_db` instance
- ChromaDB uses `PersistentClient` to store data locally
- Path is resolved relative to where the agent script runs from
- No server needed (embedded database)

**Code Reference:**
```python
# In src/vector_db.py
persist_directory = os.getenv("CHROMA_DB_PATH", "./chroma_db")
self.client = chromadb.PersistentClient(path=persist_directory)
```

## Agent Access Verification

✅ **Both databases are accessible to the agent** because:

1. **Same Directory:** Both databases are in the `agent-starter-python` directory where the agent runs
2. **Relative Paths:** Uses relative paths (`./providers.db`, `./chroma_db`) so they're always found
3. **Global Instances:** Both `db` and `vector_db` are created as global instances when modules are imported
4. **Automatic Initialization:** Databases are initialized when `search_service.py` imports them

## Current Status

- ✅ SQLite database exists: `providers.db` (100 providers)
- ✅ ChromaDB exists: `chroma_db/` directory (with embeddings)
- ✅ Agent can access both (imported via `search_service`)

## File Structure

```
agent-starter-python/
├── providers.db          # SQLite database (68KB)
├── chroma_db/           # ChromaDB vector database
│   ├── chroma.sqlite3   # ChromaDB metadata (1MB)
│   └── [collection]/    # Provider embeddings
├── src/
│   ├── database.py      # SQLite connection
│   ├── vector_db.py     # ChromaDB connection
│   ├── search_service.py # Uses both databases
│   └── agent.py         # Imports search_service
└── .env.local           # Configuration (paths)

```

## Troubleshooting

### If agent can't find databases:

1. **Check current directory:**
   ```bash
   cd /Users/shubhamsaboo/Voxology/agent-starter-python
   ```

2. **Verify databases exist:**
   ```bash
   ls -la providers.db chroma_db/
   ```

3. **Check environment variables:**
   ```bash
   cat .env.local | grep -E "(SQLITE|CHROMA)"
   ```

4. **Verify migration ran:**
   ```bash
   sqlite3 providers.db "SELECT COUNT(*) FROM providers;"
   ```

### If you need to change locations:

Edit `.env.local`:
```bash
SQLITE_DB_PATH=/custom/path/providers.db
CHROMA_DB_PATH=/custom/path/chroma_db
```

Then re-run migration:
```bash
uv run python src/migrate_data.py
```

## Access Pattern

When a user query comes in:

1. **Agent** (`agent.py`) receives query
2. **Search Service** (`search_service.py`) is called
3. **SQLite** (`database.py`) performs exact match filtering
4. **ChromaDB** (`vector_db.py`) performs semantic similarity search
5. Results are combined and returned to agent
6. Agent formats response for user

All databases are accessed synchronously during the search operation.



