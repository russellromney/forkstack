# Fork Stack Architecture

This document explains how Fork Stack achieves instant, isolated development environments.

## Core Concepts

### 1. Single Source of Truth: `.current-env`

Everything starts with a simple text file:

```bash
$ cat .current-env
alice
```

This file determines which environment all operations use. It's:
- Git-ignored (per-developer, not shared)
- Written by `make envs-switch`
- Read by `get_current_env()`

### 2. Environment Utilities

Central utilities route all operations based on current environment:

```python
def get_current_env() -> str:
    """Read .current-env file or default to 'dev'."""
    if ENV environment variable exists:
        return ENV  # For production
    if .current-env file exists:
        return file contents  # For local dev
    return 'dev'  # Default

def get_bucket_name() -> str:
    """Get environment-specific bucket."""
    env = get_current_env()
    return f"myproject-bucket-{env}"

def get_database_url() -> str:
    """Get environment-specific database."""
    env = get_current_env()
    if env == 'prod':
        return 'libsql://myproject.turso.io'
    return f'libsql://myproject-{env}.turso.io'
```

### 3. Resource Isolation

Each environment gets its own:

**Database Branch**
- Instant creation (copy-on-write)
- Independent schema and data
- Zero cost to create
- Example: `myproject-alice.turso.io`

**Storage Bucket Fork**
- Instant creation (snapshot-based)
- Independent object storage
- Zero-copy (no duplication charges)
- Example: `myproject-bucket-alice`

**Local State**
- Environment-specific directories
- Example: `myproject.alice.db/`

## Data Flow

### Creating an Environment

```
make envs-new alice
    ↓
scripts/envs.py create alice
    ↓
1. Create database branch: turso db create myproject-alice
2. Get credentials: turso db show myproject-alice --url
3. Create bucket fork: aws s3api create-bucket --bucket myproject-bucket-alice
4. Write .env.local with credentials
5. Write .current-env = "alice"
    ↓
Environment ready in ~5 seconds!
```

### Switching Environments

```
make envs-switch bob
    ↓
scripts/envs.py switch bob
    ↓
1. Verify bob environment exists
2. Get bob credentials
3. Write .env.local with bob credentials
4. Write .current-env = "bob"
    ↓
make down && make up
    ↓
App now uses bob's database, bucket, and local state
```

### Application Runtime

```
Application starts
    ↓
Import env_utils
    ↓
get_current_env() reads .current-env → "alice"
    ↓
get_bucket_name() → "myproject-bucket-alice"
get_database_url() → "libsql://myproject-alice.turso.io"
get_local_db_path() → "myproject.alice.db/"
    ↓
All operations use alice's resources
    ↓
Perfect isolation!
```

## Technology Choices

### Why Database Branching?

Traditional approaches:
- **Shared dev DB**: Developers conflict
- **DB per developer**: Expensive, slow to provision
- **Local only**: Can't test with prod-like data

Database branching gives you:
- ✅ Instant creation (copy-on-write)
- ✅ Zero cost (no duplication until writes)
- ✅ Production parity (fork from prod)
- ✅ Easy cleanup (delete instantly)

**Supported services:**
- Turso (SQLite) - Free tier, instant branches
- Neon (Postgres) - Copy-on-write branches
- PlanetScale (MySQL) - Database branching

### Why Bucket Forking?

Traditional object storage:
- **Shared bucket**: Developers conflict on keys
- **Bucket per developer**: Expensive duplication
- **Prefixes**: Complex key management

Bucket forking gives you:
- ✅ Instant creation (snapshot-based)
- ✅ Zero-copy (fork-on-write)
- ✅ Simple keys (no prefix management)
- ✅ True isolation

**Supported services:**
- Tigris - Native bucket forking support
- AWS S3 - Bucket-per-environment (not forking, but works)
- Cloudflare R2 - Bucket-per-environment

### Why Make Commands?

Commands like `make envs-new alice` provide:
- Consistent interface across projects
- Self-documenting (`make help`)
- Easy to remember
- Cross-platform (works on Mac/Linux/Windows)

## Security

### Credential Management

```
Production (Doppler/secrets manager)
    ↓
ENV=prod → get_database_url() → Production database

Development (.env.local, git-ignored)
    ↓
.current-env=alice → get_database_url() → Alice database
```

**Key points:**
- Production uses environment variables from secret manager
- Development uses `.env.local` (git-ignored)
- `.current-env` determines which credentials to use
- Never commit `.env.local` or `.current-env`

### Protected Environments

```python
PROTECTED_ENVS = ["dev", "prod"]
```

Prevents accidental deletion:
```bash
$ make envs-delete prod
✗ Cannot delete protected environment: prod
```

## Performance

### Environment Creation Speed

**Traditional approach:**
1. Provision database: 2-5 minutes
2. Copy data: 5-30 minutes
3. Set up storage: 1-2 minutes
**Total: 8-37 minutes**

**Fork Stack approach:**
1. Branch database: 1-2 seconds
2. Fork bucket: 2-3 seconds
3. Write config: <1 second
**Total: ~5 seconds**

### Storage Cost

**Traditional duplication:**
- 100GB prod data
- 3 dev environments
- Cost: 400GB = $9.20/month (AWS S3)

**Fork Stack:**
- 100GB prod data
- 3 forked environments
- Cost: ~100GB = $2.30/month (fork-on-write)

## Scaling

### Team Size

Fork Stack scales from 1 to 100+ developers:
- Each developer gets isolated environments
- No shared state or conflicts
- Instant creation encourages experimentation
- Easy cleanup keeps costs low

### CI/CD

Use Fork Stack for:
- **Preview environments**: One per PR
- **Integration testing**: Isolated test data
- **QA environments**: Stable test environments

```yaml
# GitHub Actions example
- name: Create preview environment
  run: make envs-new pr-${{ github.event.pull_request.number }}

- name: Run tests
  run: make test

- name: Cleanup
  run: make envs-delete pr-${{ github.event.pull_request.number }}
```

## Trade-offs

### Advantages
- ✅ Instant environment creation
- ✅ Perfect isolation
- ✅ Low cost
- ✅ Production parity
- ✅ Simple cleanup

### Limitations
- ⚠️ Requires services with branching/forking
- ⚠️ Some learning curve for teams
- ⚠️ Not suitable for all database engines
- ⚠️ Storage must support forking or bucket-per-env

## Future Enhancements

Possible improvements:
1. **Automatic cleanup**: Delete environments after N days inactive
2. **Environment templates**: Fork from templates, not just prod
3. **Resource limits**: Prevent runaway environment creation
4. **Monitoring**: Track environment usage and costs
5. **Collaboration**: Share environments between developers
