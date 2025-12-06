"""
Doppler secrets manager backend for forkstack.

Doppler provides environment-aware secrets management with support for
branching and per-environment secret configurations.

Setup guide: See README.md in this directory
"""
import os
import subprocess
from typing import Optional


def get_secret(key: str, environment: str = None) -> str:
    """
    Get a secret from Doppler.

    Fetches the secret from Doppler for the specified environment.
    If environment is not specified, uses the current environment
    from .current-env or ENV variable.

    Args:
        key: Secret key name (e.g., 'DATABASE_PASSWORD')
        environment: Doppler environment (if None, uses current env)

    Returns:
        Secret value
    """
    import json

    if not environment:
        # Use current environment if not specified
        from pathlib import Path

        env_var = os.getenv("ENV")
        if env_var:
            environment = env_var.lower()
        else:
            current_env_file = Path(".current-env")
            if current_env_file.exists():
                environment = current_env_file.read_text().strip()
            else:
                environment = "dev"

    # Use Doppler CLI to get the secret
    cmd = f"doppler secrets get {key} --json"

    try:
        # Set the environment context
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_ENVIRONMENT": environment},
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("value", "")
    except Exception:
        pass

    # Fall back to environment variable if secret not found
    return os.getenv(key, "")


def get_all_secrets(environment: str = None) -> dict:
    """
    Get all secrets for an environment from Doppler.

    Returns all secrets as a dictionary that can be used to populate
    environment variables or configuration.

    Args:
        environment: Doppler environment (if None, uses current env)

    Returns:
        Dictionary of key-value pairs
    """
    import json

    if not environment:
        from pathlib import Path

        env_var = os.getenv("ENV")
        if env_var:
            environment = env_var.lower()
        else:
            current_env_file = Path(".current-env")
            if current_env_file.exists():
                environment = current_env_file.read_text().strip()
            else:
                environment = "dev"

    cmd = "doppler secrets download --json"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_ENVIRONMENT": environment},
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass

    return {}


def set_secret(key: str, value: str, environment: str = None) -> bool:
    """
    Set a secret in Doppler.

    Creates or updates a secret in the specified Doppler environment.

    Args:
        key: Secret key name
        value: Secret value
        environment: Doppler environment (if None, uses current env)

    Returns:
        True if successful, False otherwise
    """
    if not environment:
        from pathlib import Path

        env_var = os.getenv("ENV")
        if env_var:
            environment = env_var.lower()
        else:
            current_env_file = Path(".current-env")
            if current_env_file.exists():
                environment = current_env_file.read_text().strip()
            else:
                environment = "dev"

    # Use Doppler CLI to set the secret
    cmd = f"doppler secrets set {key}={value}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_ENVIRONMENT": environment},
        )

        return result.returncode == 0
    except Exception:
        return False


def delete_secret(key: str, environment: str = None) -> bool:
    """
    Delete a secret from Doppler.

    Removes a secret from the specified Doppler environment.

    ⚠️ WARNING: This is irreversible.

    Args:
        key: Secret key name to delete
        environment: Doppler environment (if None, uses current env)

    Returns:
        True if successful, False otherwise
    """
    if not environment:
        from pathlib import Path

        env_var = os.getenv("ENV")
        if env_var:
            environment = env_var.lower()
        else:
            current_env_file = Path(".current-env")
            if current_env_file.exists():
                environment = current_env_file.read_text().strip()
            else:
                environment = "dev"

    cmd = f"doppler secrets delete {key}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            input="yes\n",  # Auto-confirm deletion
            env={**os.environ, "DOPPLER_ENVIRONMENT": environment},
        )

        return result.returncode == 0
    except Exception:
        return False


def create_environment(
    project: str, environment: str, description: str = None
) -> bool:
    """
    Create a new Doppler environment.

    Creates a new environment in the Doppler project for a new forkstack environment.

    Args:
        project: Doppler project name
        environment: Environment name to create
        description: Optional description for the environment

    Returns:
        True if successful, False otherwise
    """
    cmd = f"doppler environments create {environment}"
    if description:
        cmd += f" --description {description}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_PROJECT": project},
        )

        return result.returncode == 0
    except Exception:
        return False


def list_environments(project: str) -> list:
    """
    List all Doppler environments in a project.

    Args:
        project: Doppler project name

    Returns:
        List of environment names
    """
    try:
        result = subprocess.run(
            "doppler environments list",
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "DOPPLER_PROJECT": project},
        )

        if result.returncode == 0:
            # Parse output to extract environment names
            envs = []
            for line in result.stdout.split("\n"):
                parts = line.strip().split()
                if parts:
                    envs.append(parts[0])
            return envs
    except Exception:
        pass

    return []
