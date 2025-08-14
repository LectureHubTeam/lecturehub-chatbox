"""
Test script for Docker database setup.
This script tests the PostgreSQL database running in Docker with pgvector.
"""

import time

import psycopg

from src.database.database import DatabaseManager


def test_docker_database():
    """Test the Docker database setup."""

    print("Testing Docker Database Setup\n")

    # Test 1: Basic connection
    print("1. Testing basic database connection...")
    try:
        db = DatabaseManager(host="localhost", port="5432", database="embedding", user="root", password="root_password")

        if db.test_connection():
            print("   ✓ Database connection successful")
        else:
            print("   ✗ Database connection failed")
            return False
    except Exception as e:
        print(f"   ✗ Connection error: {e}")
        return False

    # Test 2: Check pgvector extension
    print("\n2. Testing pgvector extension...")
    try:
        with psycopg.connect(
            host="localhost", port="5432", database="embedding", user="root", password="root_password"
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT test_pgvector();")
                result = cur.fetchone()
                if result:
                    print(f"   ✓ {result[0]}")
                else:
                    print("   ✗ pgvector test function not found")
                    return False
    except Exception as e:
        print(f"   ✗ pgvector test failed: {e}")
        return False

    # Test 3: Test basic vector operations
    print("\n3. Testing basic vector operations...")
    try:
        with psycopg.connect(
            host="localhost", port="5432", database="embedding", user="root", password="root_password"
        ) as conn:
            with conn.cursor() as cur:
                # Test if vector extension is working
                cur.execute("SELECT '[1,2,3]'::vector;")
                result = cur.fetchone()
                if result:
                    print("   ✓ Vector operations working")
                else:
                    print("   ✗ Vector operations failed")
                    return False
    except Exception as e:
        print(f"   ✗ Vector operations test failed: {e}")
        return False

    print("\n✓ All Docker database tests passed!")
    return True


def wait_for_database(max_attempts=30):
    """Wait for database to be ready."""
    print("Waiting for database to be ready...")

    for attempt in range(max_attempts):
        try:
            with psycopg.connect(
                host="localhost", port="5432", database="embedding", user="root", password="root_password"
            ):
                print(f"   ✓ Database is ready (attempt {attempt + 1})")
                return True
        except psycopg.OperationalError:
            print(f"   Waiting... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)

    print("   ✗ Database failed to start within timeout")
    return False


if __name__ == "__main__":
    print("Docker Database Test Suite")
    print("=" * 50)

    # Wait for database to be ready
    if not wait_for_database():
        print("Database is not ready. Please ensure Docker container is running.")
        print("Run: ./docker-setup.sh start")
        exit(1)

    # Run tests
    if test_docker_database():
        print("\n🎉 All tests passed! Docker database is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the Docker setup.")
        exit(1)
