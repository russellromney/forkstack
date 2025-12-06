# Choosing a Stack

forkstack supports multiple database and storage providers. This guide helps you choose the right combination for your project.

## Quick Decision Tree

```
What database engine do you need?
├── SQLite → Turso (recommended)
├── Postgres → Neon or Supabase
└── MySQL → PlanetScale

What storage features do you need?
├── Native bucket forking → Tigris (recommended)
├── AWS ecosystem integration → S3
└── Cloudflare ecosystem → R2

Do you need secrets management?
├── Yes, with environments → Doppler (recommended)
├── Yes, AWS native → AWS Secrets Manager
└── Yes, self-hosted → HashiCorp Vault
```

## Database Comparison

### Turso (SQLite)

**Best for:** Most projects, especially those starting fresh.

| Aspect | Details |
|--------|---------|
| Engine | SQLite (libSQL) |
| Branching | Native, instant |
| Free tier | 500 databases, 9GB storage |
| Latency | Edge replicas available |
| CLI | `turso` |

```bash
# Install
brew install chiselstrike/tap/turso

# Create branch
turso db create myproject-dev
```

**Pros:**

- Simplest to set up
- SQLite is familiar and well-documented
- Branches are instant and free
- Edge replicas for low latency
- No connection pooling needed

**Cons:**

- SQLite limitations (no full-text search, limited concurrency)
- Smaller ecosystem than Postgres/MySQL
- Less suitable for high-write workloads

### Neon (Postgres)

**Best for:** Projects needing full Postgres features.

| Aspect | Details |
|--------|---------|
| Engine | PostgreSQL |
| Branching | Native, instant |
| Free tier | 3GB storage, 100 hours/month |
| Latency | Regional |
| CLI | `neonctl` |

```bash
# Install
npm install -g neonctl

# Create branch
neonctl branches create --name dev
```

**Pros:**

- Full Postgres compatibility
- Powerful branching with point-in-time restore
- Large ecosystem (extensions, ORMs, tools)
- Good for complex queries and joins

**Cons:**

- More complex than SQLite
- Connection pooling often needed
- Higher resource usage

### PlanetScale (MySQL)

**Best for:** Teams already using MySQL.

| Aspect | Details |
|--------|---------|
| Engine | MySQL (Vitess) |
| Branching | Native, instant |
| Free tier | 5GB storage, 1B reads/month |
| Latency | Regional with caching |
| CLI | `pscale` |

```bash
# Install
brew install planetscale/tap/pscale

# Create branch
pscale branch create myproject dev
```

**Pros:**

- MySQL compatibility
- Excellent branching workflow
- Good for high-read workloads
- Schema migrations built-in

**Cons:**

- Some MySQL features not supported (foreign keys need workarounds)
- Vitess abstractions can be confusing
- Pricing can increase quickly

### Supabase (Postgres)

**Best for:** Projects needing realtime features or auth.

| Aspect | Details |
|--------|---------|
| Engine | PostgreSQL |
| Branching | Via branching feature (newer) |
| Free tier | 500MB storage, 2 projects |
| Latency | Regional |
| CLI | `supabase` |

```bash
# Install
npm install -g supabase

# Create branch
supabase db branch create dev
```

**Pros:**

- Full Postgres compatibility
- Built-in auth, realtime, storage
- Good admin UI
- Growing ecosystem

**Cons:**

- Branching is newer/less mature
- More opinionated than raw Postgres
- Can be overkill for simple projects

## Storage Comparison

### Tigris

**Best for:** Most forkstack projects.

| Aspect | Details |
|--------|---------|
| Protocol | S3-compatible |
| Forking | Native bucket forks |
| Free tier | 5GB storage, 10GB transfer |
| Latency | Global edge caching |
| CLI | AWS CLI compatible |

```bash
# Create bucket
aws s3 mb s3://myproject-bucket-dev --endpoint-url https://fly.storage.tigris.dev
```

**Pros:**

- Native bucket forking (copy-on-write)
- S3-compatible API
- Global edge caching
- Cost effective

**Cons:**

- Smaller ecosystem than AWS
- Fewer regions than S3
- Newer service

### AWS S3

**Best for:** AWS ecosystem integration.

| Aspect | Details |
|--------|---------|
| Protocol | S3 (native) |
| Forking | Bucket-per-environment (not true forking) |
| Free tier | 5GB storage for 12 months |
| Latency | Regional |
| CLI | `aws` |

```bash
# Create bucket
aws s3 mb s3://myproject-bucket-dev
```

**Pros:**

- Industry standard
- Massive ecosystem
- Many regions
- Excellent reliability

**Cons:**

- No native bucket forking
- More expensive for storage
- More complex pricing

### Cloudflare R2

**Best for:** Cloudflare ecosystem integration.

| Aspect | Details |
|--------|---------|
| Protocol | S3-compatible |
| Forking | Bucket-per-environment (not true forking) |
| Free tier | 10GB storage, unlimited egress |
| Latency | Global edge |
| CLI | `wrangler` or AWS CLI |

```bash
# Create bucket
wrangler r2 bucket create myproject-bucket-dev
```

**Pros:**

- No egress fees
- S3-compatible API
- Global edge
- Cloudflare integration

**Cons:**

- No native bucket forking
- Smaller ecosystem than S3
- Cloudflare account required

## Secrets Management Comparison

### Doppler

**Best for:** Teams needing environment-aware secrets.

| Aspect | Details |
|--------|---------|
| Environments | Native support |
| Free tier | 5 users, unlimited secrets |
| Integration | CLI, SDKs, direct injection |
| CLI | `doppler` |

```bash
# Install
brew install dopplerhq/cli/doppler

# Get secret
doppler secrets get API_KEY
```

**Pros:**

- Built for environment-based secrets
- Easy team collaboration
- Good CLI and SDKs
- Secret syncing to cloud providers

**Cons:**

- External dependency
- Learning curve for teams
- Cost scales with users

### AWS Secrets Manager

**Best for:** AWS-native projects.

| Aspect | Details |
|--------|---------|
| Environments | Via naming conventions |
| Free tier | 30-day trial |
| Integration | AWS SDK, CLI |
| CLI | `aws` |

```bash
# Get secret
aws secretsmanager get-secret-value --secret-id myproject/dev/api-key
```

**Pros:**

- AWS integration
- IAM-based access control
- Automatic rotation
- Audit logging

**Cons:**

- More complex setup
- Cost per secret/API call
- Requires AWS account

### HashiCorp Vault

**Best for:** Self-hosted or enterprise.

| Aspect | Details |
|--------|---------|
| Environments | Flexible paths |
| Free tier | Self-hosted is free |
| Integration | CLI, SDKs, API |
| CLI | `vault` |

```bash
# Get secret
vault kv get secret/myproject/dev/api-key
```

**Pros:**

- Self-hosted option
- Extremely flexible
- Dynamic secrets
- Enterprise features

**Cons:**

- Complex to set up and maintain
- Overkill for small projects
- Requires infrastructure

### Environment Files

**Best for:** Simple projects or local-only development.

| Aspect | Details |
|--------|---------|
| Environments | File per environment |
| Free tier | Free |
| Integration | Native to most frameworks |
| CLI | N/A |

```bash
# .env.dev
API_KEY=dev_key_123
DATABASE_URL=libsql://myproject-dev.turso.io
```

**Pros:**

- Simple
- No external dependencies
- Works everywhere

**Cons:**

- Manual management
- No rotation
- Easy to accidentally commit

## Recommended Stacks

### For New Projects

**Python + Turso + Tigris + Doppler**

```bash
cp -r stacks/python-turso-tigris-doppler/* your-project/
```

- Simplest setup
- Best free tiers
- Native forking support

### For Postgres Projects

**Python + Neon + Tigris + Doppler**

- Full Postgres features
- Instant branching
- Good for complex data models

### For AWS Ecosystem

**Python + Neon + S3 + AWS Secrets Manager**

- AWS-native
- Familiar tools
- Good for enterprise

### For Cloudflare Ecosystem

**TypeScript + PlanetScale + R2 + Doppler**

- Edge-optimized
- No egress fees
- Good for Workers

## Cost Comparison

Estimated monthly costs for a small team (3 developers, 5 environments):

| Stack | Database | Storage | Secrets | Total |
|-------|----------|---------|---------|-------|
| Turso + Tigris + Doppler | $0 | $0 | $0 | **$0** |
| Neon + Tigris + Doppler | $0 | $0 | $0 | **$0** |
| Neon + S3 + AWS SM | $0 | $5 | $2 | **$7** |
| PlanetScale + R2 + Doppler | $0 | $0 | $0 | **$0** |

*Based on free tier limits. Costs increase with usage.*

## Migration Between Stacks

forkstack makes it relatively easy to swap backends:

1. Update `env_utils.py` with new implementation
2. Migrate data to new service
3. Update CLI commands in `envs.py`
4. Update `.env.local` with new credentials

The core pattern (`get_current_env()`, environment isolation) stays the same regardless of backend.
