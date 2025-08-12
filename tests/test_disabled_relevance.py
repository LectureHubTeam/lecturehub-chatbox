#!/usr/bin/env python3
"""
Test script to verify relevance checker is disabled.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_relevance_disabled():
    """Test that relevance checking is disabled."""
    print("Testing Relevance Checker Disabled")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Check initial status
        status = chatbot.get_system_status()
        print(f"Initial status: {status}")

        # Test various questions that would normally be rejected
        test_questions = [
            "Hello",
            "Hi there",
            "What's the weather like?",
            "Tell me a joke",
            "Random question",
            "How are you?",
            "What time is it?",
            "Test question",
            "This is not related to the lecture",
        ]

        print("\nTesting questions (should all be accepted):")
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")

            # Test relevance (if relevance checker exists)
            if chatbot.relevance_checker:
                is_relevant = chatbot.relevance_checker.is_relevant(question)
                print(f"   Relevance checker result: {is_relevant}")
            else:
                print("   Relevance checker not available")

            # Test full processing
            answer, sources, is_relevant = chatbot.process_question(question)
            print(f"   Answer: {answer[:100]}...")
            print(f"   Sources: {len(sources)}")
            print(f"   Is relevant: {is_relevant}")

            # Check if answer is not the refusal message
            refusal_msg = "Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi."
            if refusal_msg in answer:
                print(f"   ❌ Still getting refusal message!")
                return False
            else:
                print(f"   ✅ Not getting refusal message")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_with_database():
    """Test with actual database setup."""
    print("\nTesting with Database Setup")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Setup database
        print("Setting up database...")
        db_result = chatbot.setup_database(
            host="localhost", port="5432", database="embedding", user="root", password="root_password"
        )
        print(f"Database setup: {db_result}")

        # Load documents
        documents = chatbot.load_and_process_documents()
        if documents is None:
            print("❌ No documents found")
            return False

        print(f"✅ Loaded {len(documents)} documents")

        # Setup vector store
        print("Setting up vector store...")
        conn_str = "postgresql+psycopg://root:root_password@localhost:5432/embedding"
        vs_result = chatbot.setup_vectorstore(conn_str, documents, False)
        print(f"Vector store setup: {vs_result}")

        # Setup QA chain
        if vs_result:
            print("Setting up QA chain...")
            qa_result = chatbot.setup_qa_chain()
            print(f"QA chain setup: {qa_result}")

        # Test questions
        test_questions = ["Hello", "What is this about?", "Random question"]

        print("\nTesting questions with full setup:")
        for question in test_questions:
            print(f"\nQuestion: {question}")
            answer, sources, is_relevant = chatbot.process_question(question)
            print(f"Answer: {answer}")
            print(f"Sources: {len(sources)}")
            print(f"Relevant: {is_relevant}")

            # Check if answer is not the refusal message
            refusal_msg = "Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi."
            if refusal_msg in answer:
                print(f"❌ Still getting refusal message!")
                return False
            else:
                print(f"✅ Not getting refusal message")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🔧 Relevance Checker Disabled Test Suite")
    print("=" * 50)

    # Test basic relevance checker disabled
    if not test_relevance_disabled():
        print("\n❌ Basic relevance checker disabled test failed!")
        return 1

    # Test with database
    if not test_with_database():
        print("\n❌ Database test failed!")
        return 1

    print("\n🎉 All tests passed!")
    print("\nThe relevance checker is successfully disabled.")
    print("All questions should now be accepted without filtering.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
