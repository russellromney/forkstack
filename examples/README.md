# forkstack Examples

This directory contains example implementations of the forkstack pattern.

## Simple Demo

**`simple-app.py`** - Minimal example showing how environment utilities work

Run it to see how forkstack routes resources:
```bash
# Default environment (dev)
python examples/simple-app.py

# Create and switch to a personal environment
make envs-new alice
python examples/simple-app.py
# Now shows alice's resources
```

## Real-World Example

For a complete production implementation, see:

**[romneys.app](https://github.com/russellromney/romneys.app)** - Full-stack family social network
- FastAPI backend + Preact frontend
- Turso (SQLite branches)
- Tigris (S3-compatible bucket forks)
- KuzuDB (local graph database)
- Complete test suite
- Doppler secrets management
- Deployed on Fly.io

### Key files to study:
- `backend/app/env_utils.py` - Environment utilities
- `backend/scripts/envs.py` - Environment management
- `backend/Makefile` - Development commands
- `backend/tests/test_env_utils.py` - Comprehensive tests

## Contributing Examples

Have an example using forkstack? Submit a PR!

Ideas:
- Next.js + Supabase + R2
- Django + Neon + S3
- Rails + PlanetScale + Tigris
- Express + Turso + Cloudflare R2
