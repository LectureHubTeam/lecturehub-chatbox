#!/usr/bin/env python3
"""
Script to clean up the custom embeddings table.
This table is no longer needed since PGVector creates its own tables.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def cleanup_embeddings_table():
    """Remove the custom embeddings table if it exists."""
    print("🧹 Cleaning up custom embeddings table")
    print("=" * 50)

    try:
        import psycopg

        # Connect to database
        conn_str = "postgresql://root:root_password@localhost:5432/embedding"
        print(f"Connecting to database: {conn_str}")

        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Check if embeddings table exists
                print("\n1. Checking if embeddings table exists...")
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'embeddings';
                """
                )

                if cur.fetchone():
                    print("   ✓ embeddings table found")

                    # Check if table has data
                    cur.execute("SELECT COUNT(*) FROM embeddings;")
                    count = cur.fetchone()[0]
                    print(f"   - Table contains {count} records")

                    if count > 0:
                        print("   ⚠️  Table contains data. Are you sure you want to delete it?")
                        response = input("   Type 'yes' to confirm deletion: ")
                        if response.lower() != "yes":
                            print("   ❌ Deletion cancelled")
                            return False

                    # Drop the table
                    print("\n2. Dropping embeddings table...")
                    cur.execute("DROP TABLE IF EXISTS embeddings CASCADE;")
                    print("   ✓ embeddings table dropped")

                    # Check for related indexes
                    print("\n3. Checking for related indexes...")
                    cur.execute(
                        """
                        SELECT indexname
                        FROM pg_indexes
                        WHERE tablename = 'embeddings';
                    """
                    )
                    indexes = cur.fetchall()
                    if indexes:
                        print(f"   - Found {len(indexes)} related indexes (dropped with table)")
                        for index in indexes:
                            print(f"     - {index[0]}")
                    else:
                        print("   - No related indexes found")

                else:
                    print("   ✓ embeddings table does not exist (already cleaned up)")

                # Show remaining tables
                print("\n4. Current tables in database:")
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """
                )
                tables = cur.fetchall()
                for table in tables:
                    print(f"   - {table[0]}")

        print("\n🎉 Cleanup completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("🔧 Custom Embeddings Table Cleanup")
    print("=" * 50)
    print("This script will remove the custom 'embeddings' table")
    print("since PGVector creates its own tables automatically.")
    print()

    if cleanup_embeddings_table():
        print("\n✅ Cleanup successful!")
        print("PGVector will continue to work with its own tables.")
        return 0
    else:
        print("\n❌ Cleanup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
