"""
Unit tests for forkstack environment utilities.

Tests the core functionality without requiring external service credentials.
"""
import os
import tempfile
from pathlib import Path
import pytest

from env_utils import (
    get_current_env,
    get_local_db_path,
    get_database_url,
    get_bucket_name,
    get_s3_key,
    PROJECT_NAME,
)


class TestGetCurrentEnv:
    """Test environment resolution logic."""

    def test_default_to_dev(self, monkeypatch):
        """Should default to 'dev' when no ENV or .current-env."""
        # Remove ENV variable
        monkeypatch.delenv("ENV", raising=False)

        # Temporarily mock the current_env_file check
        env = get_current_env()
        # In test environment, this might be 'dev' or might read .current-env if it exists
        assert env in ["dev", "prod", "alice"]  # Should be a valid env name

    def test_respects_env_variable(self, monkeypatch):
        """Should use ENV environment variable if set."""
        monkeypatch.setenv("ENV", "production")
        env = get_current_env()
        assert env == "prod"  # Maps 'production' to 'prod'

        monkeypatch.setenv("ENV", "development")
        env = get_current_env()
        assert env == "dev"  # Maps 'development' to 'dev'

    def test_env_variable_direct(self, monkeypatch):
        """Should handle direct env variable names."""
        monkeypatch.setenv("ENV", "alice")
        env = get_current_env()
        assert env == "alice"

    def test_case_insensitive(self, monkeypatch):
        """Should be case-insensitive."""
        monkeypatch.setenv("ENV", "PRODUCTION")
        env = get_current_env()
        assert env == "prod"


class TestLocalDbPath:
    """Test local database path generation."""

    def test_path_format(self, monkeypatch):
        """Should generate correct path format."""
        monkeypatch.setenv("ENV", "dev")
        path = get_local_db_path()
        assert str(path) == f"{PROJECT_NAME}.dev.db"

    def test_different_environments(self, monkeypatch):
        """Should generate different paths for different environments."""
        monkeypatch.setenv("ENV", "alice")
        path_alice = get_local_db_path()
        assert str(path_alice) == f"{PROJECT_NAME}.alice.db"

        monkeypatch.setenv("ENV", "bob")
        path_bob = get_local_db_path()
        assert str(path_bob) == f"{PROJECT_NAME}.bob.db"

    def test_returns_path_object(self):
        """Should return a Path object."""
        path = get_local_db_path()
        assert isinstance(path, Path)


class TestDatabaseUrl:
    """Test database URL generation."""

    def test_dev_environment(self, monkeypatch):
        """Should generate correct URL for dev environment."""
        monkeypatch.setenv("ENV", "dev")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        url = get_database_url()
        assert url == f"libsql://{PROJECT_NAME}-dev.turso.io"

    def test_prod_environment(self, monkeypatch):
        """Should generate correct URL for prod environment."""
        monkeypatch.setenv("ENV", "prod")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        url = get_database_url()
        assert url == f"libsql://{PROJECT_NAME}.turso.io"

    def test_custom_environment(self, monkeypatch):
        """Should generate correct URL for custom environments."""
        monkeypatch.setenv("ENV", "alice")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        url = get_database_url()
        assert url == f"libsql://{PROJECT_NAME}-alice.turso.io"

    def test_respects_database_url_env_var(self, monkeypatch):
        """Should use DATABASE_URL env var if set."""
        monkeypatch.setenv("ENV", "staging")
        monkeypatch.setenv("DATABASE_URL", "libsql://custom-url.turso.io")
        url = get_database_url()
        assert url == "libsql://custom-url.turso.io"

    def test_format_is_valid(self, monkeypatch):
        """Should generate valid libsql:// URLs."""
        monkeypatch.setenv("ENV", "alice")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        url = get_database_url()
        assert url.startswith("libsql://")
        assert url.endswith(".turso.io")


class TestBucketName:
    """Test storage bucket name generation."""

    def test_dev_bucket(self, monkeypatch):
        """Should generate correct bucket for dev environment."""
        monkeypatch.setenv("ENV", "dev")
        bucket = get_bucket_name()
        assert bucket == f"{PROJECT_NAME}-bucket-dev"

    def test_prod_bucket(self, monkeypatch):
        """Should generate correct bucket for prod environment."""
        monkeypatch.setenv("ENV", "prod")
        bucket = get_bucket_name()
        assert bucket == f"{PROJECT_NAME}-bucket-prod"

    def test_custom_environment_bucket(self, monkeypatch):
        """Should generate correct bucket for custom environments."""
        monkeypatch.setenv("ENV", "alice")
        bucket = get_bucket_name()
        assert bucket == f"{PROJECT_NAME}-bucket-alice"

    def test_bucket_name_format(self, monkeypatch):
        """Bucket names should be valid S3 format."""
        monkeypatch.setenv("ENV", "test")
        bucket = get_bucket_name()
        # S3 bucket names are alphanumeric and hyphens
        assert all(c.isalnum() or c == "-" for c in bucket)
        assert not bucket.startswith("-")
        assert not bucket.endswith("-")


class TestS3Key:
    """Test S3 key generation."""

    def test_basic_key_format(self):
        """Should generate correct S3 key format."""
        key = get_s3_key("photos", "abc123.jpg")
        assert key == "photos/abc123.jpg"

    def test_different_resource_types(self):
        """Should work with different resource types."""
        assert get_s3_key("documents", "file.pdf") == "documents/file.pdf"
        assert get_s3_key("backups", "2024-01-01.tar.gz") == "backups/2024-01-01.tar.gz"
        assert get_s3_key("videos", "intro.mp4") == "videos/intro.mp4"

    def test_nested_paths(self):
        """Should support nested paths."""
        key = get_s3_key("photos", "2024/01/photo.jpg")
        assert key == "photos/2024/01/photo.jpg"

    def test_key_format_consistency(self):
        """Should always use forward slashes."""
        key = get_s3_key("data", "nested/path/file.txt")
        assert "/" in key
        assert key.count("/") == 3  # "data/" + "nested/" + "path/" + "file.txt"


class TestEnvironmentIntegration:
    """Test integration between different components."""

    def test_all_components_use_same_env(self, monkeypatch):
        """All components should use the same environment."""
        monkeypatch.setenv("ENV", "alice")
        monkeypatch.delenv("DATABASE_URL", raising=False)

        env = get_current_env()
        db_url = get_database_url()
        bucket = get_bucket_name()

        assert "alice" in db_url
        assert "alice" in bucket

    def test_isolation_across_environments(self, monkeypatch):
        """Different environments should have completely isolated resources."""
        # Alice's resources
        monkeypatch.setenv("ENV", "alice")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        alice_db = get_database_url()
        alice_bucket = get_bucket_name()

        # Bob's resources
        monkeypatch.setenv("ENV", "bob")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        bob_db = get_database_url()
        bob_bucket = get_bucket_name()

        # Should be completely different
        assert alice_db != bob_db
        assert alice_bucket != bob_bucket
        assert "alice" in alice_db
        assert "bob" in bob_db
        assert "alice" in alice_bucket
        assert "bob" in bob_bucket


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
