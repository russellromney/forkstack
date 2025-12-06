# Tigris Object Storage Backend for forkstack

Tigris is an S3-compatible object storage service that supports instant bucket forking—perfect for environment-isolated storage without expensive data duplication.

## Features

- **S3-compatible** - Use standard AWS S3 SDK and tools
- **Instant bucket forks** - Create isolated buckets in milliseconds
- **Zero-copy** - Forks don't duplicate data until you write
- **Global edge** - Replicate to edge locations worldwide
- **Affordable** - Storage is cheap; bandwidth is cheaper

## Prerequisites

1. **Tigris account** - Sign up at https://tigris.dev
2. **AWS CLI** - Install from https://aws.amazon.com/cli/
3. **Access credentials** - Get from your Tigris dashboard
4. **boto3** - For Python integration (optional)

## Setup

### 1. Get Your Credentials

From your Tigris dashboard:
- Access Key ID
- Secret Access Key
- (Optionally) Bucket to fork from

### 2. Configure Your Project

Add to your `.env.local`:

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ENDPOINT_URL=https://s3.tigris.dev  # Optional, if different
```

Update `PROJECT_NAME` in your `env_utils.py`:

```python
PROJECT_NAME = "myproject"
```

### 3. Install Dependencies (if using boto3)

```bash
pip install boto3
```

## Usage

### Create an environment/bucket

```bash
python envs.py create alice
# Creates: myproject-bucket-alice
```

### Access files from your app

```python
from implementations.tigris import get_s3_client

client = get_s3_client("myproject", "alice")

# Upload a file
client.upload_file("local_file.txt", "myproject-bucket-alice", "folder/file.txt")

# Download a file
client.download_file("myproject-bucket-alice", "folder/file.txt", "local_file.txt")

# List objects
response = client.list_objects_v2(Bucket="myproject-bucket-alice", Prefix="folder/")
for obj in response.get("Contents", []):
    print(obj["Key"])
```

Or with direct S3 URLs:

```python
from app.env_utils import get_bucket_name

bucket = get_bucket_name()  # myproject-bucket-alice
url = f"https://s3.tigris.dev/{bucket}/folder/file.txt"
```

### List all buckets

```bash
aws s3 ls --endpoint-url https://s3.tigris.dev
```

### Delete an environment/bucket

```bash
python envs.py delete alice
# Destroys: myproject-bucket-alice
```

## Cost Considerations

- **Bucket forks are free** - Create as many as you want
- **Storage is shared until you write** - Fork-on-write means minimal duplication
- **No per-request charges** - Unlimited operations
- **Bandwidth is cheap** - $0.02/GB (currently very affordable)
- **Edge replication** - Optional additional cost for geographic distribution

## Common Issues

### "Access Denied"

Check your credentials:

```bash
aws s3 ls --endpoint-url https://s3.tigris.dev
```

If this fails, your credentials are wrong. Re-check in your Tigris dashboard.

### "Bucket already exists"

Bucket names are globally unique. Try a different name or check if it exists:

```bash
aws s3 ls --endpoint-url https://s3.tigris.dev | grep myproject
```

### "Connection refused"

Make sure your endpoint URL is correct. Default is `https://s3.tigris.dev`.

## Documentation

- [Tigris Docs](https://www.tigrisdata.com/docs/)
- [S3 Compatibility](https://www.tigrisdata.com/docs/sdks/s3/)
- [Bucket Forking](https://www.tigrisdata.com/docs/bucket-operations/)
- [Pricing](https://www.tigrisdata.com/pricing/)

## When to Use Tigris

✅ **Good for:**
- S3-compatible applications
- Teams needing instant bucket isolation
- Cost-conscious organizations
- Global edge replication needs

❌ **Not ideal for:**
- Applications requiring non-S3 APIs
- Compliance requirements for specific cloud providers
- Applications already using AWS S3 extensively
