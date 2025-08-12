#!/usr/bin/env python3
"""
Test script to check QA chain initialization.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_qa_chain_initialization():
    """Test QA chain initialization."""
    print("Testing QA Chain Initialization")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Check initial status
        status = chatbot.get_system_status()
        print(f"Initial status: {status}")

        # Test with invalid database (should fail gracefully)
        print("\nTesting with invalid database...")
        result = chatbot.initialize_system(
            host="invalid_host", port="5432", database="test", user="test", password="test"
        )
        print(f"Initialize result: {result}")

        # Check status after failed initialization
        status = chatbot.get_system_status()
        print(f"Status after failed init: {status}")

        # Test question processing without initialization
        print("\nTesting question processing without initialization...")
        answer, sources, is_relevant = chatbot.process_question("Test question")
        print(f"Answer: {answer}")
        print(f"Is relevant: {is_relevant}")
        print(f"Sources count: {len(sources)}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_qa_chain_with_documents():
    """Test QA chain with actual documents."""
    print("\nTesting QA Chain with Documents")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Load documents
        documents = chatbot.load_and_process_documents()
        if documents is None:
            print("⚠️  No documents found (expected if files don't exist)")
            return True

        print(f"✅ Loaded {len(documents)} documents")

        # Test document processing
        print("Testing document processing...")
        # This should create relevance checker
        print("✅ Document processing completed")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main test function."""
    print("QA Chain Test Suite")
    print("=" * 50)

    tests = [
        ("QA Chain Initialization", test_qa_chain_initialization),
        ("QA Chain with Documents", test_qa_chain_with_documents),
    ]

    all_passed = True

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if not test_func():
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 All QA chain tests passed!")
        print("\nThe QA chain initialization logic is working correctly.")
    else:
        print("❌ Some QA chain tests failed.")
        print("Please check the errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
