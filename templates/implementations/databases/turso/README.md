# Turso Database Backend for forkstack

Turso provides instant SQLite database branching with zero-copy architecture—perfect for fork-on-write development environments.

## Features

- **Instant branches** - Create database branches in milliseconds, not minutes
- **Zero-copy** - Branches don't duplicate data until you write
- **SQLite-based** - No new database to learn; it's SQLite
- **Distributed** - Replicate to edge locations for faster access
- **Affordable** - Per-database pricing, not per-connection

## Prerequisites

1. **Turso account** - Sign up at https://turso.tech
2. **Turso CLI** - Install from https://turso.tech/cli
   ```bash
   brew install chiselstrike/tap/turso  # macOS
   # Or see docs for Linux/Windows
   ```
3. **API token** - Login with `turso auth login`

## Setup

### 1. Create your primary database

```bash
turso db create myproject
```

### 2. Get your database token

```bash
turso db tokens create myproject
```

This creates an authentication token. You'll need this in your `.env.local` for production.

### 3. Configure your project

Update `PROJECT_NAME` in your `env_utils.py`:

```python
PROJECT_NAME = "myproject"
```

## Usage

### Create an environment/branch

```bash
python envs.py create alice
# Creates: myproject-alice branch
```

### Switch environments

```bash
python envs.py switch alice
# Updates .current-env and .env.local
```

### List all branches

```bash
turso db list
```

### Delete an environment/branch

```bash
python envs.py delete alice
# Destroys: myproject-alice branch
```

## Database URLs

When using forkstack, your app will automatically use environment-specific URLs:

```python
from app.env_utils import get_database_url

# In dev environment:
get_database_url()  # libsql://myproject-dev.turso.io

# In alice environment:
get_database_url()  # libsql://myproject-alice.turso.io

# In production:
get_database_url()  # libsql://myproject.turso.io
```

## Connecting from Python

Use the `turso` or `tursoql` client:

```python
import tursoql

db_url = "libsql://myproject-alice.turso.io"
db_token = os.getenv("DATABASE_AUTH_TOKEN")

conn = tursoql.connect(db_url, auth_token=db_token)
result = conn.execute("SELECT * FROM users")
```

Or with SQLAlchemy:

```python
from sqlalchemy import create_engine

db_url = "libsql://myproject-alice.turso.io"
db_token = os.getenv("DATABASE_AUTH_TOKEN")

# Using the libsql protocol
engine = create_engine(f"sqlite+libsql://:@{db_url}?authToken={db_token}")
```

## Cost Considerations

- **Branches are free** - Create as many as you want
- **Storage is shared** - Branches fork-on-write, so storage grows only with changes
- **Requests are cheap** - Billed per request, not per connection
- **Replication costs** - Optional edge replication has additional cost

## Common Issues

### "turso: command not found"
Install the Turso CLI: https://turso.tech/cli

### "database not found"
Make sure you've created the database:
```bash
turso db create myproject
```

### "authentication failed"
Your token is invalid or expired. Create a new one:
```bash
turso db tokens create myproject
```

## Documentation

- [Turso Docs](https://docs.turso.tech/)
- [Database Branching Guide](https://docs.turso.tech/features/branching)
- [CLI Reference](https://docs.turso.tech/reference/turso-cli)

## When to Use Turso

✅ **Good for:**
- SQLite-based projects
- Teams needing instant database isolation
- Development environments with frequent branching
- Cost-conscious projects

❌ **Not ideal for:**
- Projects needing Postgres-specific features
- Projects already heavily invested in MySQL
- Applications requiring advanced database features beyond SQLite
