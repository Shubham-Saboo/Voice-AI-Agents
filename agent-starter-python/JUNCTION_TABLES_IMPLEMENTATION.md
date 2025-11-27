# Junction Tables Implementation

## Overview

Implemented normalized junction tables for `insurance_accepted` and `languages` to replace JSON array queries with indexed JOINs, significantly improving query performance and scalability.

## Changes Made

### 1. **database.py** - Added Junction Tables

- Created `provider_insurance` junction table with indexes on both `provider_id` and `insurance`
- Created `provider_language` junction table with indexes on both `provider_id` and `language`
- Added helper classes `ProviderInsurance` and `ProviderLanguage` for easier querying
- Kept JSON columns for backward compatibility (can be removed later)

### 2. **db_service.py** - Updated Queries to Use JOINs

**Before (Slow - LIKE queries):**
```python
# Used JSON contains (slow, no index)
conditions.append(Provider.insurance_accepted.contains([insurance]))
conditions.append(Provider.languages.contains([language]))
```

**After (Fast - Indexed JOINs):**
```python
# Uses indexed junction tables (fast!)
query = query.join(provider_insurance).filter(
    provider_insurance.c.insurance == insurance
)
query = query.join(provider_language).filter(
    provider_language.c.language == language
)
```

**Updated Methods:**
- `get_available_languages()` - Now queries junction table directly
- `get_available_insurance()` - Now queries junction table directly
- `query_providers()` - Uses JOINs instead of JSON contains
- `_provider_to_dict()` - Populates arrays from junction tables

### 3. **migrate_data.py** - Populate Junction Tables

- Updated migration to populate both `provider_insurance` and `provider_language` tables
- Each insurance/language entry creates a row in the respective junction table

## Performance Improvements

### Query Performance

**Old SQL (Slow):**
```sql
SELECT * FROM providers 
WHERE insurance_accepted LIKE '%Blue Cross Blue Shield%'
-- Full table scan, no index usage
```

**New SQL (Fast):**
```sql
SELECT DISTINCT providers.* 
FROM providers 
JOIN provider_insurance ON providers.id = provider_insurance.provider_id 
WHERE provider_insurance.insurance = 'Blue Cross Blue Shield'
-- Uses index on provider_insurance.insurance
```

### Indexes Created

- `idx_provider_insurance_insurance` - Fast insurance lookups
- `idx_provider_insurance_provider` - Fast provider lookups
- `idx_provider_language_language` - Fast language lookups
- `idx_provider_language_provider` - Fast provider lookups

## Benefits

1. **Fast Queries** - Indexed JOINs instead of full table scans
2. **Scalable** - Performance improves with proper indexes
3. **No Agent Changes** - Same function interface, better performance
4. **Normalized Data** - Proper relational structure

## Testing

All queries verified:
- ✅ Insurance filtering works (58 providers accept Blue Cross Blue Shield)
- ✅ Language filtering works
- ✅ Combined queries work (insurance + language + location)
- ✅ Available lists work correctly
- ✅ SQL uses indexed JOINs

## Migration

To apply these changes to an existing database:

1. Delete old database: `rm providers.db`
2. Run migration: `uv run python src/migrate_data.py`

The migration script will:
- Create new schema with junction tables
- Populate junction tables from JSON arrays
- Maintain backward compatibility with JSON columns

## SQL Query Example

**Query:** Find providers accepting Blue Cross Blue Shield

**Generated SQL:**
```sql
SELECT DISTINCT providers.* 
FROM providers 
JOIN provider_insurance ON providers.id = provider_insurance.provider_id 
WHERE provider_insurance.insurance = 'Blue Cross Blue Shield'
ORDER BY providers.rating DESC
LIMIT 5
```

This query uses the index on `provider_insurance.insurance` for fast lookups!

## Next Steps (Optional)

1. Remove JSON columns after confirming everything works (they're kept for backward compatibility)
2. Add more indexes if needed for other query patterns
3. Consider adding composite indexes for common query combinations

