#!/usr/bin/env python3
"""
Script to check database data and debug insertion issues.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def check_database_data():
    """Check database data."""
    print("🔍 Checking Database Data")
    print("=" * 50)

    try:
        import psycopg

        # Connect to database
        conn_str = "postgresql://root:root_password@localhost:5432/embedding"
        print(f"Connecting to database: {conn_str}")

        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:

                # Check if pgvector extension exists
                print("\n1. Checking pgvector extension...")
                cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                extensions = cur.fetchall()
                if extensions:
                    print("✅ pgvector extension is installed")
                else:
                    print("❌ pgvector extension is not installed")

                # Check tables
                print("\n2. Checking tables...")
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """
                )
                tables = cur.fetchall()
                print("Tables found:")
                for table in tables:
                    print(f"  - {table[0]}")

                # Check langchain_pg_collection table
                print("\n3. Checking langchain_pg_collection...")
                cur.execute("SELECT COUNT(*) FROM langchain_pg_collection;")
                collection_count = cur.fetchone()[0]
                print(f"Collections: {collection_count}")

                if collection_count > 0:
                    cur.execute("SELECT name, uuid FROM langchain_pg_collection;")
                    collections = cur.fetchall()
                    for collection in collections:
                        print(f"  - {collection[0]} (UUID: {collection[1]})")

                # Check langchain_pg_embedding table
                print("\n4. Checking langchain_pg_embedding...")
                cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding;")
                embedding_count = cur.fetchone()[0]
                print(f"Embeddings: {embedding_count}")

                if embedding_count > 0:
                    cur.execute(
                        """
                        SELECT e.uuid, e.document, e.cmetadata, c.name as collection_name
                        FROM langchain_pg_embedding e
                        JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                        LIMIT 5;
                    """
                    )
                    embeddings = cur.fetchall()
                    for i, embedding in enumerate(embeddings, 1):
                        print(f"  {i}. UUID: {embedding[0]}")
                        print(f"     Document: {embedding[1][:100]}...")
                        print(f"     Metadata: {embedding[2]}")
                        print(f"     Collection: {embedding[3]}")
                        print()

                # Check PostgreSQL version
                print("\n5. Checking PostgreSQL version...")
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"PostgreSQL version: {version}")

        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_document_insertion():
    """Test document insertion."""
    print("\n🧪 Testing Document Insertion")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Load documents
        documents = chatbot.load_and_process_documents()
        if documents is None:
            print("❌ No documents found")
            return False

        print(f"✅ Loaded {len(documents)} documents")

        # Show document info
        for i, doc in enumerate(documents[:3], 1):
            print(f"\nDocument {i}:")
            print(f"  Content: {doc.page_content[:100]}...")
            print(f"  Metadata: {doc.metadata}")

        # Setup database
        print("\nSetting up database...")
        db_result = chatbot.setup_database(
            host="localhost", port="5432", database="embedding", user="root", password="root_password"
        )
        print(f"Database setup: {db_result}")

        # Setup vector store
        print("\nSetting up vector store...")
        conn_str = "postgresql+psycopg://root:root_password@localhost:5432/embedding"
        vs_result = chatbot.setup_vectorstore(conn_str, documents, True)  # Force rebuild
        print(f"Vector store setup: {vs_result}")

        return True

    except Exception as e:
        print(f"❌ Document insertion test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("🔧 Database Data Check")
    print("=" * 50)

    # Check database data
    if not check_database_data():
        print("\n❌ Database check failed!")
        return 1

    # Test document insertion
    if not test_document_insertion():
        print("\n❌ Document insertion test failed!")
        return 1

    print("\n🎉 All checks completed!")
    print("\nIf you see 0 embeddings, the issue is with document insertion.")
    print("If you see embeddings but get errors, the issue is with retrieval.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
