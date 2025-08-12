#!/usr/bin/env python3
"""
Simple test to check if psycopg import works.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test if all imports work correctly."""
    print("Testing imports...")

    try:
        import psycopg

        print("✅ psycopg imported successfully")
    except ImportError as e:
        print(f"❌ psycopg import failed: {e}")
        return False

    try:
        from src.core.config import DEFAULT_CONN_STR

        print(f"✅ Config loaded: {DEFAULT_CONN_STR[:50]}...")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from src.database.database import DatabaseManager

        print("✅ DatabaseManager imported successfully")
    except Exception as e:
        print(f"❌ DatabaseManager import failed: {e}")
        return False

    return True


def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")

    try:
        from src.core.config import DEFAULT_CONN_STR
        from src.database.database import DatabaseManager

        db_manager = DatabaseManager(DEFAULT_CONN_STR)
        print(f"✅ DatabaseManager created with connection: {DEFAULT_CONN_STR[:50]}...")

        # Test connection info
        conn_info = db_manager.get_connection_info()
        print(f"✅ Connection info: {conn_info}")

        return True

    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Simple Import and Connection Test")
    print("=" * 40)

    if test_imports():
        test_database_connection()
    else:
        print("❌ Import test failed, skipping connection test")
