#!/usr/bin/env python3
"""
Environment management script for Fork Stack.

Usage:
    python envs.py create <env-name>   - Create new environment
    python envs.py switch <env-name>   - Switch to environment
    python envs.py delete <env-name>   - Delete environment
    python envs.py list                - List all environments
"""
import os
import sys
import subprocess
from pathlib import Path

# TODO: Configure these for your project
PROJECT_NAME = "myproject"
PROTECTED_ENVS = ["dev", "prod"]  # Can't be deleted

# TODO: Configure your database CLI commands
# For Turso:
DB_CLI = "turso"
DB_CREATE_CMD = lambda env: f"{DB_CLI} db create {PROJECT_NAME}-{env}"
DB_DELETE_CMD = lambda env: f"{DB_CLI} db destroy {PROJECT_NAME}-{env} -y"
DB_LIST_CMD = f"{DB_CLI} db list"
DB_URL_CMD = lambda env: f"{DB_CLI} db show {PROJECT_NAME}-{env} --url"
DB_TOKEN_CMD = lambda env: f"{DB_CLI} db tokens create {PROJECT_NAME}-{env}"

# TODO: Configure for Tigris bucket forks or your storage provider
STORAGE_CREATE_CMD = lambda env: f"aws s3api create-bucket --bucket {PROJECT_NAME}-bucket-{env}"
STORAGE_DELETE_CMD = lambda env: f"aws s3 rb s3://{PROJECT_NAME}-bucket-{env} --force"


def run_cmd(cmd, capture=True):
    """Run shell command."""
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    else:
        return subprocess.run(cmd, shell=True).returncode == 0, None


def cmd_create(env_name):
    """Create a new environment."""
    print(f"Creating environment: {env_name}")

    # 1. Create database branch
    print(f"  Creating database: {PROJECT_NAME}-{env_name}")
    success, output = run_cmd(DB_CREATE_CMD(env_name), capture=False)
    if not success:
        print(f"  ✗ Failed to create database")
        return False

    # 2. Get database credentials
    print(f"  Getting database URL...")
    success, url = run_cmd(DB_URL_CMD(env_name))
    if not success:
        print(f"  ✗ Failed to get database URL")
        return False

    print(f"  Getting database token...")
    success, token = run_cmd(DB_TOKEN_CMD(env_name))
    if not success:
        print(f"  ✗ Failed to get database token")
        return False

    # 3. Create storage bucket/fork
    print(f"  Creating storage bucket: {PROJECT_NAME}-bucket-{env_name}")
    success, _ = run_cmd(STORAGE_CREATE_CMD(env_name), capture=False)
    if not success:
        print(f"  ✗ Failed to create storage bucket")
        return False

    # 4. Write .env.local with credentials
    env_file = Path(".env.local")
    env_content = f"""# Environment: {env_name}
DATABASE_URL={url}
DATABASE_AUTH_TOKEN={token}
BUCKET_NAME={PROJECT_NAME}-bucket-{env_name}
"""
    env_file.write_text(env_content)
    print(f"  ✓ Created .env.local")

    # 5. Write .current-env
    current_env_file = Path(".current-env")
    current_env_file.write_text(env_name)
    print(f"  ✓ Set current environment to {env_name}")

    print(f"\n✓ Environment '{env_name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  1. Restart your app: make down && make up")
    print(f"  2. Your app now uses the '{env_name}' environment")
    return True


def cmd_switch(env_name):
    """Switch to an existing environment."""
    print(f"Switching to environment: {env_name}")

    # Get database credentials
    print(f"  Getting database URL...")
    success, url = run_cmd(DB_URL_CMD(env_name))
    if not success:
        print(f"  ✗ Environment '{env_name}' does not exist")
        return False

    print(f"  Getting database token...")
    success, token = run_cmd(DB_TOKEN_CMD(env_name))
    if not success:
        print(f"  ✗ Failed to get database token")
        return False

    # Update .env.local
    env_file = Path(".env.local")
    env_content = f"""# Environment: {env_name}
DATABASE_URL={url}
DATABASE_AUTH_TOKEN={token}
BUCKET_NAME={PROJECT_NAME}-bucket-{env_name}
"""
    env_file.write_text(env_content)

    # Update .current-env
    current_env_file = Path(".current-env")
    current_env_file.write_text(env_name)

    print(f"\n✓ Switched to environment '{env_name}'")
    print(f"\nNext steps:")
    print(f"  1. Restart your app: make down && make up")
    return True


def cmd_delete(env_name):
    """Delete an environment."""
    if env_name in PROTECTED_ENVS:
        print(f"✗ Cannot delete protected environment: {env_name}")
        return False

    print(f"Deleting environment: {env_name}")

    # Delete database
    print(f"  Deleting database: {PROJECT_NAME}-{env_name}")
    success, _ = run_cmd(DB_DELETE_CMD(env_name), capture=False)
    if not success:
        print(f"  ⚠ Warning: Failed to delete database")

    # Delete storage bucket
    print(f"  Deleting storage bucket: {PROJECT_NAME}-bucket-{env_name}")
    success, _ = run_cmd(STORAGE_DELETE_CMD(env_name), capture=False)
    if not success:
        print(f"  ⚠ Warning: Failed to delete storage bucket")

    # Clean up .current-env if this was the active environment
    current_env_file = Path(".current-env")
    if current_env_file.exists() and current_env_file.read_text().strip() == env_name:
        current_env_file.unlink()
        print(f"  ✓ Cleared current environment")

    print(f"\n✓ Environment '{env_name}' deleted")
    return True


def cmd_list():
    """List all environments."""
    print("Listing environments...")
    success, output = run_cmd(DB_LIST_CMD, capture=False)
    return success


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: python envs.py create <env-name>")
            sys.exit(1)
        sys.exit(0 if cmd_create(sys.argv[2]) else 1)

    elif command == "switch":
        if len(sys.argv) < 3:
            print("Usage: python envs.py switch <env-name>")
            sys.exit(1)
        sys.exit(0 if cmd_switch(sys.argv[2]) else 1)

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python envs.py delete <env-name>")
            sys.exit(1)
        sys.exit(0 if cmd_delete(sys.argv[2]) else 1)

    elif command == "list":
        sys.exit(0 if cmd_list() else 1)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
