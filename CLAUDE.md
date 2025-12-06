# Claude Development Guidelines

Guidelines for AI assistants working on this project using forkstack pattern.

## Core Principles

### 1. Use Make Commands
Always use `make` commands - never run tools directly:
```bash
make up / down / test / envs-new alice / envs-switch alice
```

### 2. Python via uv
All Python execution through `uv`:
```bash
uv run python scripts/example.py
uv run pytest tests/
```

### 3. Write Tests
- Write tests in `tests/` directory
- Run `make test` before completing features
- Tests must pass before marking task complete

### 4. Git Operations
🚨 **NEVER run git commands without explicit user permission.**
Always ask first: "Should I create a commit/push/PR?"

### 5. Secrets
- Managed in secret manager (TODO: specify yours)
- Local overrides in `.env.local` (git-ignored)
- Never commit secrets

### 6. Code Style
- Concise over verbose
- No over-engineering or premature abstractions
- Edit existing files, only Write for new files
- Watch for security vulnerabilities

## forkstack Pattern

**Environment utilities:**
```python
from app.env_utils import get_bucket_name, get_s3_key, get_current_env, get_database_url

bucket = get_bucket_name()  # myproject-bucket-dev, myproject-bucket-alice
key = get_s3_key("photos", filename)  # photos/abc123.jpg
env = get_current_env()  # dev, alice, prod
db_url = get_database_url()  # Environment-specific database URL
```

**Environment isolation:**
Each environment has its own:
- Database branch (myproject-dev, myproject-alice)
- Storage bucket fork (myproject-bucket-dev, myproject-bucket-alice)
- Local state (myproject.dev.db/, myproject.alice.db/)

## What NOT to Do

❌ Run Python without uv
❌ Run tools directly (use make commands)
❌ Git commits/push without asking
❌ Skip writing tests
❌ Delete prod/dev environments
❌ Commit secrets (.env files)
❌ Over-engineer or add unnecessary abstractions

## File Locations

**Configuration:**
- `Makefile` - All development commands
- `.env.local` - Local environment overrides (git-ignored)
- `.current-env` - Current environment (git-ignored)

**Source:**
- `app/` - Application code
- `app/env_utils.py` - Environment utilities (forkstack)
- `scripts/` - Utility scripts (envs, backups, etc.)
- `tests/` - Test suite

**Environment-specific:**
- Local database files (git-ignored)
- Remote database branches
- Remote storage bucket forks

## Quick Reference

```bash
make up                    # Start development server
make test                  # Run all tests
make envs-new alice        # Create environment named 'alice'
make envs-switch alice     # Switch to 'alice' environment
make down && make up       # Restart (after env switch)
make envs-delete alice     # Delete 'alice' environment
make help                  # All commands
```
