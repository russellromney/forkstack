# Getting Started with forkstack

This guide walks you through setting up forkstack in your project.

## Installation

```bash
curl -LsSf https://forkstack.xyz/install.sh | sh
```

Or with Cargo:

```bash
cargo install forkstack
```

## Prerequisites

You'll need accounts with:

- **Database**: [Turso](https://turso.tech) (SQLite) - get your API token from the dashboard
- **Storage** (optional): [Tigris](https://www.tigrisdata.com/) or AWS S3

## Step 1: Configure Your Project

Create `.forkstack.toml` in your project root:

```toml
[database]
provider = "turso"
organization = "your-turso-org"    # Your Turso organization name
production = "my-app-prod"         # Your production database name
group = "default"                  # Optional, defaults to "default"

# Optional: Configure storage buckets to fork
[storage.uploads]
provider = "tigris"
bucket = "my-app-uploads"
endpoint = "https://fly.storage.tigris.dev"
prefix = "forks/"

[storage.assets]
provider = "s3"
bucket = "my-app-assets"
region = "us-east-1"
prefix = "forks/"
```

## Step 2: Set Environment Variables

```bash
# Turso API token (get from Turso dashboard)
export TURSO_API_TOKEN="your-token-here"

# For S3/Tigris storage (optional)
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

## Step 3: Create Your First Fork

```bash
$ forks create
Created fork: bright-wave-42
Database: libsql://bright-wave-42-your-org.turso.io
Storage:  uploads: s3://my-app-uploads/forks/bright-wave-42/
          assets: s3://my-app-assets/forks/bright-wave-42/
```

Or with a specific name:

```bash
$ forks create -n alice
Created fork: alice
Database: libsql://alice-your-org.turso.io
Storage:  uploads: s3://my-app-uploads/forks/alice/
          assets: s3://my-app-assets/forks/alice/
```

## Step 4: Use Your Fork

Update your app's environment to use the fork:

```bash
export DATABASE_URL="libsql://alice-your-org.turso.io"
export UPLOADS_BUCKET="my-app-uploads"
export UPLOADS_PREFIX="forks/alice/"
```

Or use the fork URLs directly in your code/config.

## Step 5: List and Delete Forks

```bash
# List all forks
$ forks list
NAME            CREATED      DATABASE
bright-wave-42  5 mins ago   libsql://bright-wave-42.turso.io
alice           2 mins ago   libsql://alice.turso.io

# Delete a fork (removes database and storage)
$ forks delete alice
Deleted fork: alice
```

## Configuration Reference

### Database Section

| Field | Required | Description |
|-------|----------|-------------|
| `provider` | Yes | Database provider (`turso`) |
| `organization` | Yes | Your Turso organization name |
| `production` | Yes | Name of your production database |
| `group` | No | Turso group name (default: `default`) |

### Storage Section

You can configure multiple storage buckets. Each bucket is identified by a key (e.g., `uploads`, `assets`):

| Field | Required | Description |
|-------|----------|-------------|
| `provider` | Yes | Storage provider (`tigris`, `s3`) |
| `bucket` | Yes | Bucket name |
| `endpoint` | No | Custom S3 endpoint (for Tigris, R2, etc.) |
| `region` | No | AWS region |
| `prefix` | No | Prefix for fork data (default: `forks/`) |

## What Happens When You Fork

When you run `forks create`:

1. **Database**: Creates a new Turso database branched from your production database using Turso's [database branching API](https://docs.turso.tech/api-reference/databases/create). This is a zero-copy operation - instant regardless of database size.

2. **Storage**: For each configured bucket, copies all objects to a fork-specific prefix. This is a full copy (not zero-copy), so large buckets take longer.

When you run `forks delete`:

1. Deletes the Turso database
2. Deletes all objects under the fork prefix in each bucket

## Next Steps

- [Architecture](architecture.md) - How forkstack works under the hood
- [CI/CD Integration](cicd.md) - Using forkstack in pipelines
