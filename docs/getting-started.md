# Getting Started with Fork Stack

This guide walks you through setting up Fork Stack in your project from scratch.

## Prerequisites

- Python 3.10+ with `uv` installed
- CLI for your database service (turso, neon, or pscale)
- CLI for your storage service (aws, tigris, etc.)
- Make

## Step 1: Choose Your Stack

Fork Stack requires two services that support forking/branching:

### Database Options

Pick one:

**Turso (SQLite)** - Recommended for most projects
```bash
brew install tursodatabase/tap/turso
turso auth login
```

**Neon (Postgres)**
```bash
npm install -g neonctl
neon auth login
```

**PlanetScale (MySQL)**
```bash
brew install planetscale/tap/pscale
pscale auth login
```

### Storage Options

**Tigris (S3-compatible)** - Recommended (supports bucket forks)
```bash
# Install AWS CLI (Tigris is S3-compatible)
brew install awscli
# Configure with Tigris credentials
aws configure
```

**AWS S3**
```bash
brew install awscli
aws configure
```

**Cloudflare R2**
```bash
npm install -g wrangler
wrangler login
```

## Step 2: Copy Templates

```bash
# Create scripts directory if needed
mkdir -p scripts

# Copy core templates
cp path/to/fork-stack/templates/env_utils.py app/env_utils.py
cp path/to/fork-stack/templates/envs.py scripts/envs.py
cp path/to/fork-stack/templates/CLAUDE.md CLAUDE.md

# Append environment commands to Makefile
cat path/to/fork-stack/templates/Makefile.envs >> Makefile
```

## Step 3: Configure for Your Project

### 1. Update `app/env_utils.py`

```python
# Change PROJECT_NAME
PROJECT_NAME = "your-project-name"

# Update get_database_url() for your database service
def get_database_url() -> str:
    env = get_current_env()

    # For Turso (SQLite):
    if env == 'prod':
        return f'libsql://{PROJECT_NAME}.turso.io'
    return f'libsql://{PROJECT_NAME}-{env}.turso.io'

    # For Neon (Postgres):
    # if env == 'prod':
    #     return f'postgresql://...'
    # return f'postgresql://{PROJECT_NAME}-{env}.neon.tech'
```

### 2. Update `scripts/envs.py`

Configure the CLI commands for your services:

```python
PROJECT_NAME = "your-project-name"
PROTECTED_ENVS = ["dev", "prod"]

# For Turso:
DB_CLI = "turso"
DB_CREATE_CMD = lambda env: f"turso db create {PROJECT_NAME}-{env}"
DB_DELETE_CMD = lambda env: f"turso db destroy {PROJECT_NAME}-{env} -y"
DB_URL_CMD = lambda env: f"turso db show {PROJECT_NAME}-{env} --url"
DB_TOKEN_CMD = lambda env: f"turso db tokens create {PROJECT_NAME}-{env}"

# For Tigris/S3:
STORAGE_CREATE_CMD = lambda env: f"aws s3api create-bucket --bucket {PROJECT_NAME}-bucket-{env}"
STORAGE_DELETE_CMD = lambda env: f"aws s3 rb s3://{PROJECT_NAME}-bucket-{env} --force"
```

### 3. Update Your App Code

Replace hardcoded paths/env vars with utilities:

**Before:**
```python
bucket = os.getenv("BUCKET_NAME")
db_url = os.getenv("DATABASE_URL")
```

**After:**
```python
from app.env_utils import get_bucket_name, get_database_url

bucket = get_bucket_name()
db_url = get_database_url()
```

## Step 4: Create Production and Dev Environments

```bash
# Create prod database and bucket
make envs-new prod

# Create dev database and bucket
make envs-new dev
```

This creates:
- Database branches: `your-project`, `your-project-dev`
- Storage buckets: `your-project-bucket-prod`, `your-project-bucket-dev`
- `.current-env` file pointing to `dev`
- `.env.local` with dev credentials

## Step 5: Update .gitignore

```bash
echo ".current-env" >> .gitignore
echo ".env.local" >> .gitignore
echo "*.*.db/" >> .gitignore  # For local database files
```

## Step 6: Test It

```bash
# Verify current environment
make envs-current

# List all environments
make envs-list

# Start your app
make up

# Your app should now use dev environment
```

## Step 7: Create Your First Personal Environment

```bash
# Create personal environment
make envs-new alice

# This creates:
# - Database: your-project-alice
# - Bucket: your-project-bucket-alice
# - Local DB: your-project.alice.db/
# - Switches to alice environment

# Restart your app
make down && make up

# Now you're working in isolated 'alice' environment!
```

## Next Steps

### For Teams

1. **Document the pattern** - Share this with your team
2. **Set up CI/CD** - Use Fork Stack for preview environments
3. **Add backup scripts** - Backup prod regularly

### For Solo Developers

1. **Create feature branches** - One environment per feature
2. **Test risky changes** - Fork from prod to debug safely
3. **Clean up regularly** - Delete old environments with `make envs-delete`

## Troubleshooting

### "Database/bucket already exists"

If you get conflicts, manually check and delete:
```bash
# List databases
turso db list

# List buckets
aws s3 ls

# Delete manually
turso db destroy your-project-alice -y
aws s3 rb s3://your-project-bucket-alice --force
```

### "Wrong environment"

Check which environment is active:
```bash
make envs-current
cat .current-env
```

Switch to correct one:
```bash
make envs-switch dev
make down && make up
```

### "Can't delete prod/dev"

These are protected by default. Edit `PROTECTED_ENVS` in `scripts/envs.py` to change.

## Advanced Topics

- [Architecture Deep Dive](architecture.md) - How Fork Stack works internally
- [Database Options](databases.md) - Detailed comparison of Turso vs Neon vs PlanetScale
- [Storage Options](storage.md) - Tigris vs S3 vs R2
- [CI/CD Integration](cicd.md) - Using Fork Stack in pipelines
