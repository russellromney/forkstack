"""
Environment utilities for forkstack with Turso + Tigris + Doppler.

This is a complete, production-ready implementation that combines:
- Turso for SQLite database branching
- Tigris for S3-compatible object storage
- Doppler for secrets management

All app code should use these utilities instead of hardcoding paths or reading env vars.
"""
import os
from pathlib import Path
from typing import Optional

# TODO: Set your project name
PROJECT_NAME = "myproject"


def get_current_env() -> str:
    """
    Get the current environment name.

    Priority:
    1. ENV environment variable (for production/deployed environments)
    2. .current-env file (for local development with envs-switch)
    3. Default to 'dev'

    Returns:
        Environment name like 'dev', 'prod', 'alice', 'staging'
    """
    # Check ENV environment variable (set in production/CI)
    env_var = os.getenv("ENV")
    if env_var:
        # Map common names
        env_map = {
            "production": "prod",
            "development": "dev",
            "prod": "prod",
            "dev": "dev",
        }
        return env_map.get(env_var.lower(), env_var.lower())

    # Check .current-env file (set by envs-switch command)
    current_env_file = Path(__file__).parent.parent.parent / ".current-env"
    if current_env_file.exists():
        return current_env_file.read_text().strip()

    # Default to dev
    return "dev"


def get_local_db_path() -> Path:
    """
    Get the environment-specific local database path.

    For databases that store files locally (SQLite, KuzuDB, etc.)

    Returns:
        Path like myproject.dev.db/ or myproject.alice.db/
    """
    env = get_current_env()
    return Path(f"{PROJECT_NAME}.{env}.db")


# ============================================================================
# DATABASE (Turso)
# ============================================================================


def get_database_url() -> str:
    """
    Get the environment-specific Turso database URL.

    Turso URLs follow the pattern:
    - Production: libsql://{project-name}.turso.io
    - Other envs: libsql://{project-name}-{env}.turso.io

    Returns:
        Turso database URL string
    """
    env = get_current_env()

    # For prod, use the base database
    if env == "prod":
        return os.getenv("DATABASE_URL", f"libsql://{PROJECT_NAME}.turso.io")

    # For other envs, use branches
    # If you have per-env URLs in .env.local, prefer those
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Otherwise construct branch URL
    return f"libsql://{PROJECT_NAME}-{env}.turso.io"


def create_database_branch(parent_branch: str = "main") -> bool:
    """
    Create a new Turso database branch for the current environment.

    Args:
        parent_branch: Parent branch to fork from (default: "main")

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    env = get_current_env()

    # Turso CLI: turso db create <name>
    cmd = f"turso db create {PROJECT_NAME}-{env}"
    if parent_branch and parent_branch != "main":
        cmd += f" --from {parent_branch}"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def delete_database_branch() -> bool:
    """
    Delete the Turso database branch for the current environment.

    ⚠️ WARNING: This is irreversible.

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    env = get_current_env()

    # Turso CLI: turso db destroy <name> -y
    cmd = f"turso db destroy {PROJECT_NAME}-{env} -y"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def get_database_token() -> str:
    """
    Get an authentication token for the current Turso database branch.

    Returns:
        Database token string
    """
    import subprocess

    env = get_current_env()

    # Turso CLI: turso db tokens create <name>
    cmd = f"turso db tokens create {PROJECT_NAME}-{env}"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return ""


def list_database_branches() -> list:
    """
    List all Turso database branches for this project.

    Returns:
        List of branch names (e.g., ['myapp', 'myapp-dev', 'myapp-alice'])
    """
    import subprocess

    cmd = "turso db list"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            branches = []
            for line in result.stdout.split("\n"):
                db_name = line.strip()
                if db_name.startswith(PROJECT_NAME):
                    branches.append(db_name)
            return branches
    except Exception:
        pass

    return []


# ============================================================================
# STORAGE (Tigris)
# ============================================================================


def get_bucket_name() -> str:
    """
    Get the environment-specific Tigris bucket name.

    Returns bucket names like:
    - prod: myproject-bucket-prod
    - dev: myproject-bucket-dev
    - alice: myproject-bucket-alice
    """
    env = get_current_env()
    return f"{PROJECT_NAME}-bucket-{env}"


def create_bucket_fork(parent_bucket: Optional[str] = None) -> bool:
    """
    Create a new Tigris bucket fork for the current environment.

    Args:
        parent_bucket: Parent bucket to fork from (if None, creates empty bucket)

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    env = get_current_env()
    bucket_name = f"{PROJECT_NAME}-bucket-{env}"

    # Create bucket using AWS CLI
    cmd = f"aws s3 mb s3://{bucket_name} --endpoint-url https://s3.amazonaws.com"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def delete_bucket_fork() -> bool:
    """
    Delete the Tigris bucket for the current environment.

    ⚠️ WARNING: This is irreversible and will delete all objects.

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    bucket_name = get_bucket_name()

    # Delete bucket and all contents
    cmd = f"aws s3 rb s3://{bucket_name} --force --endpoint-url https://s3.amazonaws.com"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def get_s3_client():
    """
    Get a configured boto3 S3 client for the current Tigris bucket.

    Requires boto3: pip install boto3

    Returns:
        boto3 S3 client instance
    """
    import boto3

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Tigris uses standard S3 API with custom endpoint
    client = boto3.client(
        "s3",
        endpoint_url="https://s3.amazonaws.com",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )

    return client


def get_s3_key(resource_type: str, filename: str) -> str:
    """
    Get the S3 key for a file.

    With bucket-per-environment architecture, keys don't need environment prefixes.

    Args:
        resource_type: Type of resource (photos, documents, backups, etc.)
        filename: The filename or path within the resource type

    Returns:
        S3 key like "photos/abc123.jpg" or "backups/2024-01-01.tar.gz"
    """
    return f"{resource_type}/{filename}"


def list_buckets() -> list:
    """
    List all Tigris buckets for this project.

    Returns:
        List of bucket names
    """
    try:
        client = get_s3_client()
        response = client.list_buckets()
        buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
        # Filter to just this project
        return [b for b in buckets if b.startswith(PROJECT_NAME)]
    except Exception:
        return []


# ============================================================================
# SECRETS (Doppler)
# ============================================================================


def get_secret(key: str) -> str:
    """
    Get a secret from Doppler.

    Fetches the secret from Doppler for the current environment.

    Args:
        key: Secret key name (e.g., 'DATABASE_PASSWORD')

    Returns:
        Secret value, or empty string if not found
    """
    import subprocess
    import json

    env = get_current_env()

    # Use Doppler CLI to get the secret
    cmd = f"doppler secrets get {key} --json"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_ENVIRONMENT": env},
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("value", "")
    except Exception:
        pass

    # Fall back to environment variable if secret not found
    return os.getenv(key, "")


def get_all_secrets() -> dict:
    """
    Get all secrets for the current environment from Doppler.

    Returns all secrets as a dictionary that can be used to populate
    environment variables or configuration.

    Returns:
        Dictionary of key-value pairs
    """
    import subprocess
    import json

    env = get_current_env()

    cmd = "doppler secrets download --json"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_ENVIRONMENT": env},
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass

    return {}


def set_secret(key: str, value: str) -> bool:
    """
    Set a secret in Doppler for the current environment.

    Args:
        key: Secret key name
        value: Secret value

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    env = get_current_env()

    # Use Doppler CLI to set the secret
    cmd = f"doppler secrets set {key}={value}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_ENVIRONMENT": env},
        )

        return result.returncode == 0
    except Exception:
        return False
