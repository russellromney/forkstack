# forkstack

**Instant, isolated development environments using zero-copy database and storage forks.**

forkstack is a pattern for creating fully isolated development environments in seconds. Each developer gets their own copy of your entire stack—database, object storage, and local state—without duplicating data or slowing down.

## Why forkstack?

Traditional development environments share databases or require expensive duplication:
- ❌ **Shared dev DB**: Developers step on each other's data
- ❌ **DB per developer**: Expensive, slow to provision, hard to keep in sync
- ❌ **Local-only**: Can't test with production-like data

forkstack gives you the best of all worlds:
- ✅ **Instant creation**: New environments in seconds, not minutes
- ✅ **Zero cost**: Fork-on-write means no data duplication charges
- ✅ **Full isolation**: Each environment has its own DB, storage, and state
- ✅ **Production parity**: Fork from production to test with real data
- ✅ **Easy cleanup**: Delete environments instantly when done

## How It Works

forkstack uses three key technologies:

1. **Database branching** - Services like Turso, Neon, or PlanetScale that support instant branches
2. **Storage forking** - Tigris bucket forks (or bucket-per-environment)
3. **Environment utilities** - Central code that routes all operations to the current environment

```
make envs-new alice
# Creates in ~5 seconds:
# - Database branch (alice)
# - Storage bucket fork (myapp-alice)
# - Local state directory (myapp.alice.db/)
# - Environment config (.current-env = alice)

make envs-switch alice
make up
# Your app now reads/writes to alice's isolated environment
```

## Architecture

```
.current-env file (git-ignored)
    ↓
get_current_env() reads file
    ↓
get_database_url() → {project}-{env}.turso.io
get_bucket_name()  → {project}-bucket-{env}
get_local_path()   → {project}.{env}.db/
    ↓
All app code uses these utilities
    ↓
Perfect isolation per environment
```

## Quick Start

### 1. Choose Your Stack

forkstack works with any combination of:

**Databases** (pick one):
- [Turso](https://turso.tech) - SQLite branches (recommended)
- [Neon](https://neon.tech) - Postgres branches
- [PlanetScale](https://planetscale.com) - MySQL branches

**Object Storage** (pick one):
- [Tigris](https://www.tigrisdata.com) - S3-compatible with bucket forks (recommended)
- AWS S3 - Bucket-per-environment
- Cloudflare R2 - Bucket-per-environment

### 2. Copy Templates

Copy the templates that match your stack:
```bash
cp templates/env_utils.py your-project/app/
cp templates/Makefile.envs your-project/Makefile  # Or append to existing
cp templates/envs.py your-project/scripts/
cp templates/claude.md your-project/
```

### 3. Configure

Update the templates with your project name:
```python
# env_utils.py
PROJECT_NAME = "your-project"

def get_bucket_name():
    env = get_current_env()
    return f"{PROJECT_NAME}-bucket-{env}"
```

### 4. Use It

```bash
# Create new environment
make envs-new alice

# Switch to it
make envs-switch alice
make down && make up

# Work in isolation
# ... make changes, test, etc ...

# Delete when done
make envs-delete alice
```

## Repository Structure

forkstack uses a hybrid organization for maximum flexibility:

```
templates/
├── base/{language}/           # Core pattern for each language
│   └── python/               # ✅ Abstract base with plugin points
├── implementations/           # Pluggable backends
│   ├── databases/
│   │   └── turso/            # ✅ SQLite branching
│   ├── storage/
│   │   └── tigris/           # ✅ S3-compatible bucket forks
│   └── secrets/
│       └── doppler/          # ✅ Environment-aware secrets
└── stacks/
    └── python-turso-tigris-doppler/  # ✅ Pre-built complete stack
```

**Three ways to use forkstack:**

1. **Grab a pre-built stack** (Recommended) - Copy entire `stacks/python-turso-tigris-doppler/`
2. **Mix and match** (Advanced) - Combine `base/python/` + implementations you want
3. **Contribute** - Add new languages, databases, or storage backends

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for the full roadmap and architecture.

## Real-World Example

See `examples/romneys-app/` for a complete FastAPI + Preact implementation using:
- Turso for SQLite database branches
- Tigris for S3-compatible bucket forks
- KuzuDB for local graph database
- Make commands for environment management

## Pattern Benefits

### For Individual Developers
- Test risky changes in isolation
- Work on multiple features simultaneously
- Fork from prod to debug with real data
- Clean up experiments instantly

### For Teams
- No database conflicts between developers
- Easy code review with deployable branches
- Staging environments on-demand
- Safe production debugging

### For Organizations
- Ephemeral preview environments
- Cost-effective testing at scale
- Compliance-friendly data isolation
- Simplified environment management

## Requirements

- Database service with branching support
- Object storage (with forking or bucket-per-environment)
- CLI tool for your database (turso, neon, pscale, etc.)
- Make (or adapt commands to your build tool)

## Documentation

- [Getting Started Guide](docs/getting-started.md) - Step-by-step setup
- [Architecture Deep Dive](docs/architecture.md) - How it works
- [Database Options](docs/databases.md) - Turso vs Neon vs PlanetScale
- [Storage Options](docs/storage.md) - Tigris vs S3 vs R2
- [Troubleshooting](docs/troubleshooting.md) - Common issues

## Migration Path

If you previously used the old template structure:

### Old Way
```bash
cp templates/env_utils.py your-project/
cp templates/envs.py your-project/
```

### New Way (Recommended)
```bash
# Complete, production-ready stack
cp -r stacks/python-turso-tigris-doppler/* your-project/
```

### Mix and Match (Advanced)
```bash
# Base template
cp templates/base/python/env_utils.py your-project/app/

# Add implementations you want
cp templates/implementations/databases/turso/python.py your-project/
cp templates/implementations/storage/tigris/python.py your-project/
cp templates/implementations/secrets/doppler/python.py your-project/

# Merge implementations into env_utils.py
```

The old templates remain available but are now marked as reference implementations. Use the new pre-built stacks or mix-and-match approach for cleaner, more modular code.

## Contributing

forkstack is a pattern, not a framework. Feel free to:
- Share your implementation
- Improve the templates
- Add support for new databases/storage
- Submit issues and improvements

## License

Apache 2.0 - Use it however you want

## Credits

Pattern developed while building [romneys.app](https://github.com/russellromney/romneys.app), a family social network with full environment isolation.
