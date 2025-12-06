# forkstack - Base Python Template

This is the core pattern for Python projects using forkstack.

## What's Included

- `env_utils.py` - Abstract base class with plugin points for:
  - `get_database_url()` - Environment-specific database URL
  - `get_bucket_name()` - Environment-specific storage bucket
  - `get_secret(key)` - Fetch secrets from your secrets manager

## How to Use

### Option 1: Use a Pre-Built Stack (Recommended)

If you want a complete, batteries-included stack:

```bash
cp -r stacks/python-turso-tigris-doppler/* your-project/
```

This gives you everything set up for Turso + Tigris + Doppler.

### Option 2: Mix and Match (Advanced)

If you want to customize which backends you use:

1. Copy the base template:
```bash
cp templates/base/python/env_utils.py your-project/app/
```

2. Copy the implementations you want:
```bash
cp templates/implementations/databases/turso/python.py your-project/implementations/
cp templates/implementations/storage/tigris/python.py your-project/implementations/
cp templates/implementations/secrets/doppler/python.py your-project/implementations/
```

3. Merge the implementations into `env_utils.py`:

```python
# app/env_utils.py
from env_utils_base import EnvConfig, get_current_env, get_local_db_path
from implementations.turso import get_database_url
from implementations.tigris import get_bucket_name
from implementations.doppler import get_secret

class MyEnvConfig(EnvConfig):
    def get_database_url(self) -> str:
        return get_database_url(PROJECT_NAME, get_current_env())

    def get_bucket_name(self) -> str:
        return get_bucket_name(PROJECT_NAME, get_current_env())

    def get_secret(self, key: str) -> str:
        return get_secret(key)

# Create global instance
config = MyEnvConfig()

# Your app uses it like:
# from app.env_utils import config
# db_url = config.get_database_url()
```

## What You Need to Implement

- **Database backend**: Implement `get_database_url()`
- **Storage backend**: Implement `get_bucket_name()`
- **Secrets backend**: Implement `get_secret(key)`

## Available Backends

See the `templates/implementations/` directory for all available:

- **Databases**: Turso, Neon, PlanetScale
- **Storage**: Tigris, S3, R2
- **Secrets**: Doppler, AWS Secrets Manager, HashiCorp Vault

## Next Steps

1. Choose your backends (database, storage, secrets)
2. Either copy a pre-built stack or mix-and-match implementations
3. Update `PROJECT_NAME` in `env_utils.py`
4. Run your first environment: `make envs-new dev`

## Questions?

See [docs/stacks/choosing.md](../../docs/stacks/choosing.md) for help choosing which backends to use.
