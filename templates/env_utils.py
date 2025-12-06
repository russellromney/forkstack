"""
Environment utilities for Fork Stack pattern.

This module provides environment-aware resource resolution.
All app code should use these utilities instead of hardcoding paths or reading env vars directly.
"""
import os
from pathlib import Path

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
    env_var = os.getenv('ENV')
    if env_var:
        # Map common names
        env_map = {
            'production': 'prod',
            'development': 'dev',
            'prod': 'prod',
            'dev': 'dev',
        }
        return env_map.get(env_var.lower(), env_var.lower())

    # Check .current-env file (set by envs-switch command)
    current_env_file = Path(__file__).parent.parent / ".current-env"
    if current_env_file.exists():
        return current_env_file.read_text().strip()

    # Default to dev
    return 'dev'


def get_bucket_name() -> str:
    """
    Get the environment-specific bucket name.

    Returns bucket names like:
    - prod: myproject-bucket-prod
    - dev: myproject-bucket-dev
    - alice: myproject-bucket-alice
    """
    env = get_current_env()
    return f"{PROJECT_NAME}-bucket-{env}"


def get_database_url() -> str:
    """
    Get the environment-specific database URL.

    This assumes you're using a database service with branching (Turso, Neon, PlanetScale).
    Override this if you have a different pattern.

    Returns URLs like:
    - prod: PROJECT_NAME.turso.io
    - dev: PROJECT_NAME-dev.turso.io
    - alice: PROJECT_NAME-alice.turso.io
    """
    env = get_current_env()

    # For prod, use the base database
    if env == 'prod':
        return os.getenv('DATABASE_URL', f'libsql://{PROJECT_NAME}.turso.io')

    # For other envs, use branches
    # If you have per-env URLs in .env.local, prefer those
    env_url = os.getenv('DATABASE_URL')
    if env_url:
        return env_url

    # Otherwise construct branch URL
    return f'libsql://{PROJECT_NAME}-{env}.turso.io'


def get_local_db_path() -> Path:
    """
    Get the environment-specific local database path.

    For databases that store files locally (SQLite, KuzuDB, etc.)
    Returns paths like:
    - myproject.dev.db/
    - myproject.alice.db/
    """
    env = get_current_env()
    return Path(f"{PROJECT_NAME}.{env}.db")


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
