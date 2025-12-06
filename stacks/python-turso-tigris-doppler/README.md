# forkstack - Python + Turso + Tigris + Doppler

A complete, production-ready environment isolation stack for Python applications.

**Features:**
- ✅ **Instant database isolation** - Turso SQLite branching
- ✅ **Zero-copy storage** - Tigris S3-compatible bucket forks
- ✅ **Centralized secrets** - Doppler environment-aware secrets
- ✅ **One-command setup** - Create new isolated environments instantly
- ✅ **Zero-cost forks** - Copy-on-write means minimal duplication charges

## Quick Start

### 1. Prerequisites

You need accounts and CLIs for:

- **Turso** - https://turso.tech (SQLite database)
  ```bash
  brew install chiselstrike/tap/turso
  turso auth login
  ```

- **Tigris** - https://tigris.dev (S3-compatible storage)
  ```bash
  aws s3 ls --endpoint-url https://s3.amazonaws.com
  ```

- **Doppler** - https://doppler.com (secrets manager)
  ```bash
  brew install dopplerhq/cli/doppler
  doppler login
  ```

### 2. Copy This Stack to Your Project

```bash
cp -r stacks/python-turso-tigris-doppler/* your-project/
```

### 3. Update Project Name

Edit `env_utils.py`:

```python
PROJECT_NAME = "your-project-name"
```

Also update environment variables in `.env.local`.

### 4. Create Your First Environment

```bash
# Create production database
turso db create your-project-name

# Create dev environment
make envs-new dev

# Create a development fork
make envs-new alice
```

### 5. Use It in Your App

```python
from env_utils import (
    get_current_env,
    get_database_url,
    get_bucket_name,
    get_secret,
)

# Current environment: dev, alice, prod, etc.
env = get_current_env()  # "alice"

# Database connection
db_url = get_database_url()  # libsql://your-project-alice.turso.io
auth_token = get_secret("DATABASE_AUTH_TOKEN")

# Storage bucket
bucket = get_bucket_name()  # your-project-bucket-alice

# Any secret from Doppler
api_key = get_secret("API_KEY")
```

## File Structure

```
.
├── env_utils.py           # Core environment utilities
├── envs.py               # CLI for creating/switching environments
├── Makefile              # Make commands for environment management
├── test_env_utils.py     # Unit tests
├── .env.local            # Environment-specific config (git-ignored)
├── .current-env          # Current environment name (git-ignored)
└── example/
    └── app.py            # Minimal example application
```

## Make Commands

### Create a new environment

```bash
make envs-new alice
# Creates:
# - Database branch: your-project-alice
# - Storage bucket: your-project-bucket-alice
# - Doppler environment: alice
# - .env.local with all credentials
```

### Switch to an environment

```bash
make envs-switch alice
# Updates .current-env and .env.local
```

### Delete an environment

```bash
make envs-delete alice
# Deletes database branch, storage bucket, keeps Doppler env for backup
```

### List all environments

```bash
make envs-list
```

## How It Works

### Current Environment Resolution

The app determines which environment to use (priority order):

1. `ENV` environment variable (for production)
2. `.current-env` file (for local development)
3. Default to `dev`

### Database (Turso)

Each environment gets its own SQLite database branch:

```python
get_database_url()
# dev:   libsql://your-project-dev.turso.io
# alice: libsql://your-project-alice.turso.io
# prod:  libsql://your-project.turso.io
```

No data duplication—Turso uses zero-copy branching.

### Storage (Tigris)

Each environment gets its own S3-compatible bucket:

```python
get_bucket_name()
# dev:   your-project-bucket-dev
# alice: your-project-bucket-alice
# prod:  your-project-bucket-prod
```

Upload/download using boto3 or AWS CLI.

### Secrets (Doppler)

Each environment has its own secrets in Doppler:

```python
get_secret("API_KEY")
# Automatically fetches from current environment's Doppler settings
```

When you create a new environment, secrets are copied from production.

## Integration with Your App

### For FastAPI

```python
from fastapi import FastAPI
from env_utils import get_database_url, get_bucket_name, get_secret

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Connect to environment-specific database
    db_url = get_database_url()
    # Connect to Turso with libsql-client-python

    # Set up S3 client for environment-specific bucket
    bucket = get_bucket_name()
```

### For Django

```python
# settings.py
from env_utils import get_database_url, get_bucket_name, get_secret

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': get_database_url(),
    }
}

# Storage
DEFAULT_FILE_STORAGE = 's3'
AWS_STORAGE_BUCKET_NAME = get_bucket_name()
```

### For SQLAlchemy

```python
from sqlalchemy import create_engine
from env_utils import get_database_url, get_secret

db_url = get_database_url()
auth_token = get_secret("DATABASE_AUTH_TOKEN")

engine = create_engine(
    f"sqlite+libsql://:@{db_url}?authToken={auth_token}"
)
```

## Testing Environments

Each developer can have their own isolated environment:

```bash
# Alice's environment
make envs-new alice
make envs-switch alice
make down && make up

# Bob's environment
make envs-new bob
make envs-switch bob
make down && make up

# Back to dev
make envs-switch dev
make down && make up
```

No conflicts, no shared state, instant cleanup:

```bash
make envs-delete alice
```

## Cost Analysis

### Storage

- **Turso branches**: Free (zero-copy)
- **Tigris buckets**: Minimal (fork-on-write)
- **Doppler secrets**: Included in free tier or Pro ($15/month)

**Total**: ~$0-15/month for unlimited environments

### Versus Alternatives

| Approach | Setup Time | Isolation | Cost |
|----------|-----------|-----------|------|
| Shared dev DB | 1 min | None | $0 |
| DB per developer | 5 min | Full | $100+/month |
| forkstack | 30 sec | Full | $0-15/month |

## Troubleshooting

### "turso: command not found"

Install Turso CLI: https://turso.tech/cli

### "authentication failed" (Doppler)

Re-authenticate:

```bash
doppler logout
doppler login
```

### "bucket already exists"

Bucket names are globally unique. Check if it exists:

```bash
aws s3 ls --endpoint-url https://s3.amazonaws.com
```

### Storage credentials not working

Check your AWS credentials:

```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

Update in `.env.local` if needed.

## Next Steps

1. **Read the docs** - See `docs/` for detailed guides
2. **Try an example** - Run `example/app.py`
3. **Create your first env** - `make envs-new alice`
4. **Integrate with your app** - Use `env_utils` in your code

## Documentation

- [Base Template Guide](../../templates/base/python/README.md)
- [Turso Setup](../../templates/implementations/databases/turso/README.md)
- [Tigris Setup](../../templates/implementations/storage/tigris/README.md)
- [Doppler Setup](../../templates/implementations/secrets/doppler/README.md)

## Architecture

See `docs/architecture.md` for detailed explanation of how forkstack works.

## Contributing

This is a template stack. Feel free to:

- Customize for your needs
- Add additional backends
- Share your modifications
- Report issues

## License

This template is Apache 2.0. Use it however you want!
