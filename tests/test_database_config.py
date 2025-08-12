"""
Test script for the new database configuration features.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from src.database.database import DatabaseManager


def test_database_config():
    """Test different database configuration methods."""

    print("Testing Database Configuration Methods\n")

    # Method 1: Using individual parameters
    print("1. Testing with individual parameters:")
    db1 = DatabaseManager(host="localhost", port="5432", database="embedding", user="root", password="root_password")
    print(f"   Connection info: {db1.get_connection_info()}")

    # Method 2: Using connection string
    print("\n2. Testing with connection string:")
    conn_str = "postgresql+psycopg://root:root_password@localhost:5432/embedding"
    db2 = DatabaseManager(connection_string=conn_str)
    print(f"   Connection info: {db2.get_connection_info()}")

    # Method 3: Using config defaults
    print("\n3. Testing with config defaults:")
    db3 = DatabaseManager()
    print(f"   Connection info: {db3.get_connection_info()}")

    # Test connection
    print("\n4. Testing database connection:")
    if db1.test_connection():
        print("   ✓ Database connection successful")
    else:
        print("   ✗ Database connection failed")

    print("\nConfiguration test completed!")


def test_env_loading():
    """Test environment variable loading."""
    print("\nTesting Environment Variable Loading:")

    print(f"DB_HOST: {DB_HOST}")
    print(f"DB_PORT: {DB_PORT}")
    print(f"DB_NAME: {DB_NAME}")
    print(f"DB_USER: {DB_USER}")
    print(f"DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'Not set'}")


if __name__ == "__main__":
    test_env_loading()
    test_database_config()
