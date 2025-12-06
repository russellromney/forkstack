#!/usr/bin/env python3
"""
Minimal example application using forkstack.

This demonstrates how to use the environment utilities in a real application.

Usage:
    python example_app.py
"""
from env_utils import (
    get_current_env,
    get_database_url,
    get_bucket_name,
    get_secret,
    get_s3_key,
)


def main():
    print("forkstack Example Application")
    print("=" * 50)

    # Get current environment
    env = get_current_env()
    print(f"\nCurrent environment: {env}")

    # Database URL
    db_url = get_database_url()
    print(f"Database URL: {db_url}")
    print("  (Connect using: libsql-client-python or sqlite3)")

    # Storage bucket
    bucket = get_bucket_name()
    print(f"\nStorage bucket: {bucket}")
    print("  (Upload files using: boto3 or aws s3 commands)")

    # Example S3 keys
    photo_key = get_s3_key("photos", "profile.jpg")
    print(f"  Example photo key: {photo_key}")

    doc_key = get_s3_key("documents", "2024/report.pdf")
    print(f"  Example doc key: {doc_key}")

    # Secrets example
    print(f"\nSecrets (from Doppler):")
    try:
        secret = get_secret("API_KEY")
        if secret:
            print(f"  API_KEY: {secret[:10]}..." if len(secret) > 10 else f"  API_KEY: {secret}")
        else:
            print(f"  API_KEY: (not set)")
    except Exception as e:
        print(f"  API_KEY: (error: {e})")

    # Example database connection (requires libsql library)
    print(f"\nExample: Connecting to database")
    print(f"  from env_utils import get_database_url, get_secret")
    print(f"  import libsql_client")
    print(f"  ")
    print(f"  db_url = get_database_url()")
    print(f"  token = get_secret('DATABASE_AUTH_TOKEN')")
    print(f"  ")
    print(f"  client = libsql_client.create_client(db_url, auth_token=token)")
    print(f"  result = client.execute('SELECT * FROM users')")

    # Example storage operations
    print(f"\nExample: Using storage")
    print(f"  from env_utils import get_s3_client, get_s3_key")
    print(f"  ")
    print(f"  s3 = get_s3_client()")
    print(f"  bucket = get_bucket_name()")
    print(f"  key = get_s3_key('photos', 'my_photo.jpg')")
    print(f"  ")
    print(f"  s3.upload_file('local_file.jpg', bucket, key)")
    print(f"  s3.download_file(bucket, key, 'downloaded_file.jpg')")

    print("\n" + "=" * 50)
    print(f"✓ Environment isolation is working!")
    print(f"  Each environment ({env}) has isolated:")
    print(f"  - Database: {db_url}")
    print(f"  - Storage: s3://{bucket}/")
    print(f"  - Secrets: Doppler {env} environment")


if __name__ == "__main__":
    main()
