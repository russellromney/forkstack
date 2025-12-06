"""
Turso database backend for forkstack.

Turso provides instant SQLite database branching with zero-copy architecture.
Perfect for fork-on-write development environments.

Setup guide: See README.md in this directory
"""


def get_database_url(project_name: str, env: str) -> str:
    """
    Get the Turso database URL for an environment.

    Turso URLs follow the pattern:
    - Production: libsql://{project-name}.turso.io
    - Other envs: libsql://{project-name}-{env}.turso.io

    Args:
        project_name: Your project name (e.g., 'myapp')
        env: Environment name (e.g., 'dev', 'alice', 'prod')

    Returns:
        Turso database URL string
        Example: libsql://myapp-alice.turso.io
    """
    if env == 'prod':
        return f'libsql://{project_name}.turso.io'
    return f'libsql://{project_name}-{env}.turso.io'


def create_branch(project_name: str, env: str, parent_branch: str = "main") -> bool:
    """
    Create a new Turso database branch.

    Uses the Turso CLI to create a new database branch.
    The branch is typically created as a clone of the parent branch.

    Args:
        project_name: Your project name
        env: Environment/branch name to create
        parent_branch: Parent branch to fork from (default: "main")

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    # Turso CLI: turso db create <name>
    # For branches: turso db create <name> --from <parent>
    cmd = f"turso db create {project_name}-{env}"
    if parent_branch and parent_branch != "main":
        cmd += f" --from {parent_branch}"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def delete_branch(project_name: str, env: str) -> bool:
    """
    Delete a Turso database branch.

    Uses the Turso CLI to destroy a database branch.
    This will delete the branch and all its data.

    ⚠️ WARNING: This is irreversible. Make sure you're deleting the right environment.

    Args:
        project_name: Your project name
        env: Environment/branch name to delete

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    # Turso CLI: turso db destroy <name> -y
    # The -y flag skips the confirmation prompt
    cmd = f"turso db destroy {project_name}-{env} -y"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def get_database_token(project_name: str, env: str) -> str:
    """
    Get an authentication token for a Turso database branch.

    Creates a new API token that can be used to connect to the database.
    The token has full read/write access to the database.

    Args:
        project_name: Your project name
        env: Environment/branch name

    Returns:
        Database token string
    """
    import subprocess

    # Turso CLI: turso db tokens create <name>
    cmd = f"turso db tokens create {project_name}-{env}"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return ""


def list_branches(project_name: str) -> list:
    """
    List all Turso database branches for a project.

    Returns all branches that match the project name pattern.

    Args:
        project_name: Your project name

    Returns:
        List of branch names (e.g., ['myapp', 'myapp-dev', 'myapp-alice'])
    """
    import subprocess

    # Turso CLI: turso db list
    cmd = "turso db list"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            # Parse output and filter to matching project
            branches = []
            for line in result.stdout.split('\n'):
                db_name = line.strip()
                if db_name.startswith(project_name):
                    branches.append(db_name)
            return branches
    except Exception:
        pass

    return []
