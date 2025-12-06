# Storage Options

Detailed comparison of object storage services for forkstack.

## Overview

forkstack works best with storage that supports bucket forking or easy bucket-per-environment patterns.

| Storage | Protocol | Forking | Free Tier | Best For |
|---------|----------|---------|-----------|----------|
| [Tigris](#tigris) | S3-compatible | Native | 5GB, 10GB transfer | Most projects |
| [AWS S3](#aws-s3) | S3 | Bucket-per-env | 5GB (12 months) | AWS ecosystem |
| [Cloudflare R2](#cloudflare-r2) | S3-compatible | Bucket-per-env | 10GB, free egress | No egress fees |

## Tigris

**S3-compatible object storage with native bucket forking.**

### Setup

```bash
# Install AWS CLI (Tigris is S3-compatible)
brew install awscli

# Configure with Tigris credentials
aws configure
# Use your Tigris access key and secret

# Create bucket
aws s3 mb s3://myproject-bucket-dev --endpoint-url https://fly.storage.tigris.dev

# Fork bucket (copy-on-write)
# Tigris supports native bucket forking via API
```

### Pros

- Native bucket forking (copy-on-write)
- S3-compatible API
- Global edge caching
- Cost effective
- No egress fees within Fly.io

### Cons

- Smaller ecosystem than AWS
- Fewer regions than S3
- Newer service

### Pricing

- Free: 5GB storage, 10GB transfer/month
- Pay-as-you-go after

---

## AWS S3

**The industry standard for object storage.**

### Setup

```bash
# Install AWS CLI
brew install awscli

# Configure
aws configure

# Create bucket
aws s3 mb s3://myproject-bucket-dev

# No native forking - use bucket-per-environment
```

### Pros

- Industry standard
- Massive ecosystem
- Many regions
- Excellent reliability
- Advanced features (versioning, lifecycle, etc.)

### Cons

- No native bucket forking
- Egress fees can add up
- More complex pricing

### Pricing

- Free: 5GB for 12 months (new accounts)
- Standard: ~$0.023/GB storage, $0.09/GB egress

---

## Cloudflare R2

**S3-compatible storage with zero egress fees.**

### Setup

```bash
# Option 1: Wrangler CLI
npm install -g wrangler
wrangler login
wrangler r2 bucket create myproject-bucket-dev

# Option 2: AWS CLI with R2 endpoint
aws s3 mb s3://myproject-bucket-dev \
  --endpoint-url https://[account-id].r2.cloudflarestorage.com
```

### Pros

- Zero egress fees
- S3-compatible API
- Global edge via Cloudflare
- Good for high-bandwidth use cases

### Cons

- No native bucket forking
- Smaller ecosystem than S3
- Requires Cloudflare account

### Pricing

- Free: 10GB storage, unlimited egress
- Standard: $0.015/GB storage, $0 egress

---

## Choosing Storage

```
Do you need...
├── Native bucket forking → Tigris
├── AWS ecosystem integration → S3
├── Zero egress fees → R2
└── Cloudflare Workers integration → R2
```

## forkstack Patterns

### With Native Forking (Tigris)

```python
# Bucket forks share data until written
# myproject-bucket-prod (100GB)
# myproject-bucket-dev  (0GB - fork, no duplication)
# myproject-bucket-alice (0GB - fork, no duplication)

bucket = get_bucket_name()  # "myproject-bucket-alice"
# Reads from prod data, writes go to alice's bucket
```

### Without Native Forking (S3, R2)

```python
# Each environment gets its own bucket
# myproject-bucket-prod (100GB)
# myproject-bucket-dev  (empty or synced)
# myproject-bucket-alice (empty or synced)

bucket = get_bucket_name()  # "myproject-bucket-alice"
# Completely independent bucket
```

For non-forking storage, you may want to:

1. Start with empty buckets (fastest)
2. Sync specific data from prod when needed
3. Use a seed script for test data

See [Choosing a Stack](choosing-a-stack.md) for the full decision tree.
