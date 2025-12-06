# Database Options

Detailed comparison of database services that support branching for forkstack.

## Overview

forkstack requires a database that supports instant branching or forking. This enables zero-copy environment creation.

| Database | Engine | Branching | Free Tier | Best For |
|----------|--------|-----------|-----------|----------|
| [Turso](#turso) | SQLite | Native | 500 DBs, 9GB | Most projects |
| [Neon](#neon) | Postgres | Native | 3GB, 100hrs | Postgres features |
| [PlanetScale](#planetscale) | MySQL | Native | 5GB, 1B reads | MySQL teams |
| [Supabase](#supabase) | Postgres | Newer | 500MB, 2 projects | Realtime/Auth |

## Turso

**SQLite with edge replication and instant branching.**

### Setup

```bash
# Install CLI
brew install chiselstrike/tap/turso

# Authenticate
turso auth login

# Create database
turso db create myproject

# Create branch
turso db create myproject-dev --from-db myproject
```

### Pros

- Simplest setup and mental model
- SQLite is familiar and well-documented
- Branches are instant and free
- Edge replicas for low latency
- No connection pooling needed

### Cons

- SQLite limitations (limited concurrency for writes)
- Smaller ecosystem than Postgres/MySQL
- Less suitable for high-write workloads

### Pricing

- Free: 500 databases, 9GB storage, 1B reads/month
- Pro: $29/month for more

---

## Neon

**Serverless Postgres with branching and autoscaling.**

### Setup

```bash
# Install CLI
npm install -g neonctl

# Authenticate
neonctl auth

# Create project
neonctl projects create --name myproject

# Create branch
neonctl branches create --name dev
```

### Pros

- Full Postgres compatibility
- Powerful branching with point-in-time restore
- Autoscaling to zero
- Large ecosystem

### Cons

- More complex than SQLite
- Connection pooling often needed
- Cold starts on scale-to-zero

### Pricing

- Free: 0.5GB storage, 100 compute hours/month
- Pro: $19/month base + usage

---

## PlanetScale

**MySQL-compatible database built on Vitess.**

### Setup

```bash
# Install CLI
brew install planetscale/tap/pscale

# Authenticate
pscale auth login

# Create database
pscale database create myproject

# Create branch
pscale branch create myproject dev
```

### Pros

- MySQL compatibility
- Excellent branching workflow
- Built-in schema migrations
- Good for high-read workloads

### Cons

- Some MySQL features not supported (foreign keys need workarounds)
- Vitess abstractions can be confusing
- Pricing can increase quickly

### Pricing

- Free: 5GB storage, 1B reads, 10M writes/month
- Scaler: $29/month + usage

---

## Supabase

**Postgres with built-in auth, realtime, and storage.**

### Setup

```bash
# Install CLI
npm install -g supabase

# Login
supabase login

# Create project (via dashboard)
# Create branch
supabase db branch create dev
```

### Pros

- Full Postgres compatibility
- Built-in auth, realtime, storage
- Good admin UI
- Growing ecosystem

### Cons

- Branching is newer/less mature
- More opinionated than raw Postgres
- Can be overkill for simple projects

### Pricing

- Free: 500MB, 2 projects
- Pro: $25/month per project

---

## Choosing a Database

```
Do you need...
├── Simplicity + edge performance → Turso
├── Full Postgres features → Neon
├── MySQL compatibility → PlanetScale
└── Auth + Realtime built-in → Supabase
```

See [Choosing a Stack](choosing-a-stack.md) for the full decision tree.
