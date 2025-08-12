#!/usr/bin/env python3
"""
Test script to check PGVector API compatibility.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_pgvector_import():
    """Test PGVector import and basic functionality."""
    print("Testing PGVector API...")

    try:
        from langchain_postgres import PGVector

        print("✅ Successfully imported PGVector")

        # Check the class attributes
        print(f"PGVector class: {PGVector}")
        print(f"PGVector.__init__ signature: {PGVector.__init__}")

        # Try to create an instance with minimal parameters
        try:
            # This should fail but give us info about the expected parameters
            vs = PGVector()
            print("✅ PGVector() with no parameters works")
        except TypeError as e:
            print(f"❌ PGVector() error: {e}")
            print("This is expected - we need to provide parameters")

        return True

    except ImportError as e:
        print(f"❌ Failed to import PGVector: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_connection_string_format():
    """Test different connection string formats."""
    print("\nTesting connection string formats...")

    connection_strings = [
        "postgresql+psycopg://user:pass@localhost:5432/db",
        "postgresql://user:pass@localhost:5432/db",
        "postgresql+psycopg://user:pass@localhost:5432/db",
    ]

    for conn_str in connection_strings:
        print(f"Testing: {conn_str}")
        # We can't actually connect without a real database, but we can check if the format is valid


def main():
    """Main test function."""
    print("PGVector API Test")
    print("=" * 50)

    if test_pgvector_import():
        test_connection_string_format()
        print("\n✅ PGVector import test completed")
    else:
        print("\n❌ PGVector import test failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
