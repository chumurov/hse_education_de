# Data Model: Разработка микросервисов TODO и ShortURL

## TODO Service

### Entity: Task

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique identifier |
| `title` | String | Not Null, Max Length 200 | Task title |
| `description` | String | Optional | Task details |
| `completed` | Boolean | Default `False` | Completion status |

**DDL (SQLite):**
```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT 0
);
```

## ShortURL Service

### Entity: URLMapping

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `short_id` | String | Primary Key, Unique | The short code (e.g., "abc12") |
| `full_url` | String | Not Null | The original long URL |
| `created_at` | DateTime | Default Current Timestamp | Creation time (optional but good for stats) |
| `clicks` | Integer | Default 0 | Click counter (for stats) |

**DDL (SQLite):**
```sql
CREATE TABLE IF NOT EXISTS urls (
    short_id TEXT PRIMARY KEY,
    full_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clicks INTEGER DEFAULT 0
);
```

## Storage Strategy

- **TODO Service**: `/app/data/todo.db`
- **ShortURL Service**: `/app/data/shorturl.db`
- **Persistence**: Docker volume mounted at `/app/data`.
