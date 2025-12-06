"""
Simple example showing forkstack pattern in action.

This demonstrates how environment utilities automatically route to the
correct resources based on .current-env file.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'templates'))

from env_utils import (
    get_current_env,
    get_bucket_name,
    get_database_url,
    get_local_db_path,
    get_s3_key
)


def main():
    """Show how forkstack routes resources."""
    print("=" * 60)
    print("forkstack Environment Demo")
    print("=" * 60)

    # Get current environment
    env = get_current_env()
    print(f"\nCurrent environment: {env}")

    # Show database routing
    db_url = get_database_url()
    print(f"\nDatabase URL: {db_url}")

    # Show storage routing
    bucket = get_bucket_name()
    print(f"Storage bucket: {bucket}")

    # Show local path routing
    local_path = get_local_db_path()
    print(f"Local DB path: {local_path}")

    # Show S3 key generation
    photo_key = get_s3_key("photos", "vacation.jpg")
    backup_key = get_s3_key("backups", "2024-01-01.tar.gz")
    print(f"\nS3 keys:")
    print(f"  Photo: {photo_key}")
    print(f"  Backup: {backup_key}")

    print("\n" + "=" * 60)
    print("All operations automatically use the correct resources!")
    print("=" * 60)

    print(f"""
To switch environments:
  1. Run: make envs-switch alice
  2. Restart your app
  3. All operations now use 'alice' environment

To create new environment:
  1. Run: make envs-new bob
  2. New isolated environment created in ~5 seconds
  3. Database: myproject-bob
  4. Bucket: myproject-bucket-bob
  5. Local DB: myproject.bob.db/
""")


if __name__ == "__main__":
    main()
