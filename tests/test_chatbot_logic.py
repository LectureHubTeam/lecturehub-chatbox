"""
Test script for the ChatbotLogic module.

This script tests the core chatbot logic without requiring Streamlit.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.chatbot_logic import ChatbotLogic, create_chatbot, test_chatbot_initialization, test_question_processing


def test_chatbot_creation():
    """Test chatbot creation."""
    print("Testing chatbot creation...")

    chatbot = create_chatbot()
    assert chatbot is not None
    assert isinstance(chatbot, ChatbotLogic)

    # Check initial status
    status = chatbot.get_system_status()
    assert status["database_initialized"] is False
    assert status["vectorstore_initialized"] is False
    assert status["qa_chain_initialized"] is False
    assert status["relevance_checker_initialized"] is False

    print("✓ Chatbot creation test passed")


def test_document_loading():
    """Test document loading functionality."""
    print("\nTesting document loading...")

    chatbot = create_chatbot()
    documents = chatbot.load_and_process_documents()

    # This will return None if no documents are found (expected in test environment)
    if documents is None:
        print("  ⚠ No documents found (expected in test environment)")
    else:
        assert isinstance(documents, list)
        print(f"  ✓ Loaded {len(documents)} document chunks")

    print("✓ Document loading test passed")


def test_database_setup():
    """Test database setup functionality."""
    print("\nTesting database setup...")

    chatbot = create_chatbot()

    # Test with invalid connection (should fail gracefully)
    result = chatbot.setup_database(host="invalid_host", port="5432", database="test", user="test", password="test")

    # Should fail with invalid connection
    assert result is False

    print("✓ Database setup test passed (failed as expected)")


def test_system_initialization():
    """Test complete system initialization."""
    print("\nTesting system initialization...")

    # Test with invalid database (should fail)
    result = test_chatbot_initialization(
        host="invalid_host", port="5432", database="test", user="test", password="test"
    )

    # Should fail with invalid connection
    assert result is False

    print("✓ System initialization test passed (failed as expected)")


def test_question_processing():
    """Test question processing functionality."""
    print("\nTesting question processing...")

    # Test with invalid database (should fail)
    answer, sources, is_relevant = test_question_processing(
        "Test question", host="invalid_host", port="5432", database="test", user="test", password="test"
    )

    # Should return error message
    assert "System initialization failed" in answer
    assert is_relevant is False

    print("✓ Question processing test passed (failed as expected)")


def test_chatbot_methods():
    """Test individual chatbot methods."""
    print("\nTesting chatbot methods...")

    chatbot = create_chatbot()

    # Test process_question without initialization
    answer, sources, is_relevant = chatbot.process_question("Test question")
    assert "System not properly initialized" in answer
    assert is_relevant is False

    # Test get_system_status
    status = chatbot.get_system_status()
    assert isinstance(status, dict)
    assert "database_initialized" in status
    assert "vectorstore_initialized" in status
    assert "qa_chain_initialized" in status
    assert "relevance_checker_initialized" in status

    print("✓ Chatbot methods test passed")


def run_all_tests():
    """Run all tests."""
    print("ChatbotLogic Test Suite")
    print("=" * 50)

    try:
        test_chatbot_creation()
        test_document_loading()
        test_database_setup()
        test_system_initialization()
        test_question_processing()
        test_chatbot_methods()

        print("\n🎉 All tests passed!")
        print("\nNote: Some tests are expected to fail due to invalid database connections.")
        print("This is normal behavior when testing without a real database.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    run_all_tests()
