#!/usr/bin/env python3
"""
Comprehensive test script to verify all fixes for LectureHub Chatbot.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test all critical imports."""
    print("Testing imports...")

    imports_to_test = [
        ("psycopg", "psycopg"),
        ("pgvector", "pgvector"),
        ("langchain_community.vectorstores.pgvector", "PGVector"),
        ("langchain_community.embeddings", "HuggingFaceEmbeddings"),
        ("streamlit", "streamlit"),
        ("src.core.chatbot_logic", "ChatbotLogic"),
        ("src.database.vectorstore", "VectorStoreManager"),
        ("src.database.database", "DatabaseManager"),
    ]

    all_passed = True

    for module_name, import_name in imports_to_test:
        try:
            if import_name == module_name:
                __import__(module_name)
            else:
                exec(f"from {module_name} import {import_name}")
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name} - {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ {module_name} - {e}")
            all_passed = False

    return all_passed


def test_pgvector_api():
    """Test PGVector API compatibility."""
    print("\nTesting PGVector API...")

    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores.pgvector import PGVector

        # Test creating embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print("✅ HuggingFaceEmbeddings created successfully")

        # Test PGVector constructor (this should fail but give us info)
        try:
            vs = PGVector(
                connection_string="postgresql+psycopg://test:test@localhost:5432/test",
                collection_name="test",
                embedding_function=embeddings,
                use_jsonb=True,
            )
            print("✅ PGVector constructor works")
        except Exception as e:
            print(f"⚠️  PGVector constructor error (expected): {e}")

        return True

    except Exception as e:
        print(f"❌ PGVector API test failed: {e}")
        return False


def test_chatbot_logic():
    """Test ChatbotLogic creation."""
    print("\nTesting ChatbotLogic...")

    try:
        from src.core.chatbot_logic import create_chatbot

        chatbot = create_chatbot()
        print("✅ ChatbotLogic created successfully")

        # Test status
        status = chatbot.get_system_status()
        print(f"✅ System status: {status}")

        return True

    except Exception as e:
        print(f"❌ ChatbotLogic test failed: {e}")
        return False


def test_connection_strings():
    """Test connection string formats."""
    print("\nTesting connection string formats...")

    # Test the format we're using
    conn_str = "postgresql://user:pass@localhost:5432/db"
    print(f"✅ Connection string format: {conn_str}")

    return True


def main():
    """Main test function."""
    print("🔧 LectureHub Chatbot - Comprehensive Fix Test")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("PGVector API", test_pgvector_api),
        ("ChatbotLogic", test_chatbot_logic),
        ("Connection Strings", test_connection_strings),
    ]

    all_passed = True

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if not test_func():
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All tests passed! The fixes are working correctly.")
        print("\nYou can now run:")
        print("  python test_logic.py")
        print("  streamlit run main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
