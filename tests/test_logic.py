#!/usr/bin/env python3
"""
Simple test script for the chatbot logic.

This script can be run directly to test the core chatbot functionality
without requiring Streamlit or complex setup.
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.core.chatbot_logic import ChatbotLogic, create_chatbot


def test_basic_functionality():
    """Test basic chatbot functionality."""
    print("Testing ChatbotLogic Basic Functionality")
    print("=" * 50)

    # Create chatbot instance
    print("1. Creating chatbot instance...")
    chatbot = create_chatbot()
    print("   ✓ Chatbot created successfully")

    # Check initial status
    print("\n2. Checking initial status...")
    status = chatbot.get_system_status()
    print(f"   Database initialized: {status['database_initialized']}")
    print(f"   Vector store initialized: {status['vectorstore_initialized']}")
    print(f"   QA chain initialized: {status['qa_chain_initialized']}")
    print(f"   Relevance checker initialized: {status['relevance_checker_initialized']}")

    # Test document loading
    print("\n3. Testing document loading...")
    documents = chatbot.load_and_process_documents()
    if documents is None:
        print("   ⚠ No documents found (expected if files don't exist)")
    else:
        print(f"   ✓ Loaded {len(documents)} document chunks")

    # Test question processing without initialization
    print("\n4. Testing question processing without initialization...")
    answer, sources, is_relevant = chatbot.process_question("Test question")
    print(f"   Answer: {answer}")
    print(f"   Is relevant: {is_relevant}")
    print(f"   Sources count: {len(sources)}")

    print("\n✅ Basic functionality test completed!")


def test_database_connection():
    """Test database connection (will fail without real database)."""
    print("\nTesting Database Connection")
    print("=" * 50)

    chatbot = create_chatbot()

    # Test with invalid connection
    print("1. Testing with invalid database connection...")
    result = chatbot.setup_database(host="invalid_host", port="5432", database="test", user="test", password="test")
    print(f"   Result: {result} (expected: False)")

    # Test with localhost (might work if database is running)
    print("\n2. Testing with localhost connection...")
    result = chatbot.setup_database(
        host="localhost", port="5432", database="embedding", user="root", password="root_password"
    )
    print(f"   Result: {result}")

    if result:
        print("   ✓ Database connection successful!")
    else:
        print("   ⚠ Database connection failed (expected if no database)")

    print("\n✅ Database connection test completed!")


def interactive_test():
    """Interactive test mode."""
    print("\nInteractive Test Mode")
    print("=" * 50)
    print("Type 'quit' to exit")

    chatbot = create_chatbot()

    while True:
        try:
            question = input("\nEnter a question: ").strip()
            if question.lower() in ["quit", "exit", "q"]:
                break

            if not question:
                continue

            print("Processing question...")
            answer, sources, is_relevant = chatbot.process_question(question)

            print(f"Answer: {answer}")
            print(f"Relevant: {is_relevant}")
            print(f"Sources: {len(sources)}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main test function."""
    print("LectureHub Chatbot Logic Test")
    print("=" * 50)

    try:
        test_basic_functionality()
        test_database_connection()

        # Ask if user wants interactive mode
        response = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
        if response in ["y", "yes"]:
            interactive_test()

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
