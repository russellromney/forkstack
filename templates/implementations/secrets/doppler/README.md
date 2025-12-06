# Doppler Secrets Manager Backend for forkstack

Doppler is a universal secrets manager that makes it easy to manage secrets across environments with support for environment branching—perfect for forkstack.

## Features

- **Environment-aware** - Different secrets per environment
- **No sprawl** - Central management of all secrets
- **Easy branching** - Clone secrets from production to new environments
- **Secure by default** - Encryption, audit logs, access control
- **Multi-framework** - Works with any language and framework

## Prerequisites

1. **Doppler account** - Sign up at https://doppler.com
2. **Doppler CLI** - Install from https://docs.doppler.com/docs/cli
   ```bash
   brew install dopplerhq/cli/doppler  # macOS
   # Or see docs for Linux/Windows
   ```
3. **Authentication** - Run `doppler login` and authenticate

## Setup

### 1. Create Your Doppler Project

```bash
doppler projects create myproject
```

### 2. Create Environments

By default, Doppler creates "dev" and "prod" environments. Create additional ones:

```bash
doppler environments create alice --description "Alice's dev environment"
```

### 3. Add Secrets

For production:

```bash
doppler secrets set DATABASE_PASSWORD --scope prod
doppler secrets set API_KEY --scope prod
```

For dev (or copy from prod):

```bash
doppler secrets set DATABASE_PASSWORD --scope dev
doppler secrets set API_KEY --scope dev
```

### 4. Configure Your Project

Add to your `.env.local`:

```bash
DOPPLER_PROJECT=myproject
DOPPLER_TOKEN=your_doppler_token  # Service token for automated access
```

Or authenticate with:

```bash
doppler login
```

## Usage

### Get a Secret in Python

```python
from implementations.doppler import get_secret

# Automatically uses current environment
password = get_secret("DATABASE_PASSWORD")
```

### Get All Secrets

```python
from implementations.doppler import get_all_secrets

secrets = get_all_secrets()
# Returns: {"DATABASE_PASSWORD": "...", "API_KEY": "...", ...}

# Use in your app
os.environ.update(secrets)
```

### Set a Secret

```bash
doppler secrets set API_KEY=your_value
```

Or in Python:

```python
from implementations.doppler import set_secret

set_secret("API_KEY", "your_value")
```

### Create a New Environment

When you create a forkstack environment, you should create a corresponding Doppler environment:

```bash
doppler environments create alice --description "Alice's fork"
```

Then copy secrets from production or dev:

```bash
doppler secrets download --environment prod > prod-secrets.json
doppler secrets upload prod-secrets.json --environment alice
```

## Integration with envs.py

You can extend `envs.py` to automatically create Doppler environments:

```python
def cmd_create(env_name):
    """Create a new environment."""
    print(f"Creating environment: {env_name}")

    # ... create database, storage, etc ...

    # Create Doppler environment
    print(f"  Creating Doppler environment...")
    from implementations.doppler import create_environment
    create_environment("myproject", env_name)

    # Copy secrets from prod
    import subprocess
    subprocess.run(
        f"doppler secrets download --environment prod > /tmp/secrets.json",
        shell=True,
    )
    subprocess.run(
        f"doppler secrets upload /tmp/secrets.json --environment {env_name}",
        shell=True,
    )

    print(f"  ✓ Created Doppler environment")
    return True
```

## Cost Considerations

- **Free tier** - 5 projects, limited secrets and team members
- **Pro** - Starts at $15/month per user
- **Team/Enterprise** - Custom pricing for larger teams
- **Service tokens** - Required for CI/CD or automated access

## Common Issues

### "doppler: command not found"

Install the Doppler CLI: https://docs.doppler.com/docs/cli

### "authentication required"

Run `doppler login` to authenticate:

```bash
doppler login
```

### "environment not found"

Create the environment first:

```bash
doppler environments create alice
```

### "cannot access secret"

Make sure you've added the secret to the environment:

```bash
doppler secrets set SECRET_NAME --scope alice
```

## Documentation

- [Doppler Docs](https://docs.doppler.com/)
- [CLI Reference](https://docs.doppler.com/docs/cli)
- [Environments Guide](https://docs.doppler.com/docs/environments)
- [Secrets Management](https://docs.doppler.com/docs/secrets)

## When to Use Doppler

✅ **Good for:**
- Teams needing centralized secrets management
- Multi-environment applications
- Compliance/audit requirements
- Teams that want to avoid .env file management

❌ **Not ideal for:**
- Solo developers wanting simple local secrets
- Highly sensitive classified/government work (consider HashiCorp Vault)
- Projects that can't afford additional services
