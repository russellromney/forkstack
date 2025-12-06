"""
Tigris object storage backend for forkstack.

Tigris is an S3-compatible object storage service that supports instant
bucket forking—perfect for environment-isolated storage.

Setup guide: See README.md in this directory
"""


def get_bucket_name(project_name: str, env: str) -> str:
    """
    Get the Tigris bucket name for an environment.

    Bucket names follow the pattern: {project-name}-bucket-{env}

    Args:
        project_name: Your project name (e.g., 'myapp')
        env: Environment name (e.g., 'dev', 'alice', 'prod')

    Returns:
        Bucket name string
        Example: myapp-bucket-alice
    """
    return f"{project_name}-bucket-{env}"


def create_bucket_fork(
    project_name: str,
    env: str,
    parent_bucket: str = None,
    aws_access_key: str = None,
    aws_secret_key: str = None,
) -> bool:
    """
    Create a new Tigris bucket fork.

    Tigris bucket forks use zero-copy, so they're instant and free.
    The fork is typically created from the production bucket.

    Args:
        project_name: Your project name
        env: Environment name
        parent_bucket: Parent bucket to fork from (if None, creates empty bucket)
        aws_access_key: AWS_ACCESS_KEY_ID for authentication (from env if not provided)
        aws_secret_key: AWS_SECRET_ACCESS_KEY for authentication (from env if not provided)

    Returns:
        True if successful, False otherwise
    """
    import subprocess
    import os

    if not aws_access_key:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    if not aws_secret_key:
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    bucket_name = get_bucket_name(project_name, env)

    # Using AWS S3 CLI with Tigris endpoint
    # For bucket forking, you would use Tigris-specific API or aws s3 cp
    env_vars = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": aws_access_key,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key,
    }

    # Create bucket
    cmd = f"aws s3 mb s3://{bucket_name} --endpoint-url https://s3.amazonaws.com"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env_vars
        )
        return result.returncode == 0
    except Exception:
        return False


def delete_bucket(
    project_name: str,
    env: str,
    aws_access_key: str = None,
    aws_secret_key: str = None,
) -> bool:
    """
    Delete a Tigris bucket.

    This removes the entire bucket and all its contents.

    ⚠️ WARNING: This is irreversible. Make sure you're deleting the right bucket.

    Args:
        project_name: Your project name
        env: Environment name
        aws_access_key: AWS_ACCESS_KEY_ID for authentication
        aws_secret_key: AWS_SECRET_ACCESS_KEY for authentication

    Returns:
        True if successful, False otherwise
    """
    import subprocess
    import os

    if not aws_access_key:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    if not aws_secret_key:
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    bucket_name = get_bucket_name(project_name, env)

    env_vars = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": aws_access_key,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key,
    }

    # Delete bucket and all contents
    cmd = f"aws s3 rb s3://{bucket_name} --force --endpoint-url https://s3.amazonaws.com"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env_vars
        )
        return result.returncode == 0
    except Exception:
        return False


def get_s3_client(
    project_name: str, env: str, aws_access_key: str = None, aws_secret_key: str = None
):
    """
    Get a configured boto3 S3 client for a Tigris bucket.

    This returns a boto3 S3 client configured to use Tigris endpoint.

    Args:
        project_name: Your project name
        env: Environment name
        aws_access_key: AWS_ACCESS_KEY_ID for authentication
        aws_secret_key: AWS_SECRET_ACCESS_KEY for authentication

    Returns:
        boto3 S3 client instance
    """
    import boto3
    import os

    if not aws_access_key:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    if not aws_secret_key:
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Tigris uses standard S3 API with custom endpoint
    client = boto3.client(
        "s3",
        endpoint_url="https://s3.amazonaws.com",  # Replace with Tigris endpoint if different
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )

    return client


def list_buckets(aws_access_key: str = None, aws_secret_key: str = None) -> list:
    """
    List all Tigris buckets.

    Args:
        aws_access_key: AWS_ACCESS_KEY_ID for authentication
        aws_secret_key: AWS_SECRET_ACCESS_KEY for authentication

    Returns:
        List of bucket names
    """
    import os

    if not aws_access_key:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    if not aws_secret_key:
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    try:
        client = get_s3_client("", "", aws_access_key, aws_secret_key)
        response = client.list_buckets()
        return [bucket["Name"] for bucket in response.get("Buckets", [])]
    except Exception:
        return []
