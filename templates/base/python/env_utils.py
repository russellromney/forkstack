"""
Base environment utilities for forkstack pattern.

This abstract base class defines the plugin points for forkstack implementations.
All backends (Turso, Neon, PlanetScale, etc.) implement these methods.

Core (implemented here):
- get_current_env() - Reads from .current-env or ENV variable

Plugin points (implemented by backends):
- get_database_url() - Returns database URL for current environment
- get_bucket_name() - Returns storage bucket name for current environment
- get_secret() - Returns secret from configured secrets manager
"""
import os
from pathlib import Path
from abc import ABC, abstractmethod


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
    current_env_file = Path(__file__).parent.parent.parent / ".current-env"
    if current_env_file.exists():
        return current_env_file.read_text().strip()

    # Default to dev
    return 'dev'


def get_local_db_path() -> Path:
    """
    Get the environment-specific local database path.

    For databases that store files locally (SQLite, KuzuDB, etc.)

    Returns:
        Path like myproject.dev.db/ or myproject.alice.db/
    """
    env = get_current_env()
    return Path(f"{PROJECT_NAME}.{env}.db")


class EnvConfig(ABC):
    """
    Abstract base class for forkstack environment configuration.

    Subclass this and implement the abstract methods to support your
    database, storage, and secrets backends.
    """

    @abstractmethod
    def get_database_url(self) -> str:
        """
        Get the environment-specific database URL.

        Returns:
            Database URL for current environment
            Examples:
            - libsql://myproject-dev.turso.io (Turso)
            - postgresql://user:pass@host/db (Neon/PlanetScale)
        """
        pass

    @abstractmethod
    def get_bucket_name(self) -> str:
        """
        Get the environment-specific storage bucket name.

        Returns:
            Bucket name like myproject-bucket-dev or myproject-bucket-alice
        """
        pass

    @abstractmethod
    def get_secret(self, key: str) -> str:
        """
        Get a secret from the configured secrets manager.

        Args:
            key: Secret key/name

        Returns:
            Secret value
        """
        pass

    def get_s3_key(self, resource_type: str, filename: str) -> str:
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
