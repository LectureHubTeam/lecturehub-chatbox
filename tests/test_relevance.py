#!/usr/bin/env python3
"""
Test script to check relevance checker functionality.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_relevance_checker():
    """Test relevance checker."""
    print("Testing Relevance Checker")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Load documents to create relevance checker
        documents = chatbot.load_and_process_documents()
        if documents is None:
            print("⚠️  No documents found, creating mock relevance checker")
            # Create a mock relevance checker that always returns True
            from src.llm.keyword_extractor import RelevanceChecker

            chatbot.relevance_checker = RelevanceChecker(set())
        else:
            print(f"✅ Loaded {len(documents)} documents")

        # Test various questions
        test_questions = [
            "What is this lecture about?",
            "Explain the main concepts",
            "How does this work?",
            "What are the key points?",
            "Can you help me understand this?",
            "Tell me about the code",
            "What is the problem?",
            "Hello",
            "Hi there",
            "Test question",
            "Random question about nothing",
        ]

        print("\nTesting questions:")
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")

            # Test relevance
            if chatbot.relevance_checker:
                is_relevant = chatbot.relevance_checker.is_relevant(question)
                print(f"   Relevant: {is_relevant}")
            else:
                print("   Relevance checker not available")

            # Test full processing
            answer, sources, is_relevant = chatbot.process_question(question)
            print(f"   Answer: {answer[:100]}...")
            print(f"   Sources: {len(sources)}")
            print(f"   Is relevant: {is_relevant}")

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
        test_questions = ["What is this lecture about?", "Explain the main concepts", "How does this work?"]

        print("\nTesting questions with full setup:")
        for question in test_questions:
            print(f"\nQuestion: {question}")
            answer, sources, is_relevant = chatbot.process_question(question)
            print(f"Answer: {answer}")
            print(f"Sources: {len(sources)}")
            print(f"Relevant: {is_relevant}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🔧 Relevance Checker Test Suite")
    print("=" * 50)

    # Test basic relevance checker
    if not test_relevance_checker():
        print("\n❌ Basic relevance checker test failed!")
        return 1

    # Test with database
    if not test_with_database():
        print("\n❌ Database test failed!")
        return 1

    print("\n🎉 All relevance checker tests passed!")
    print("\nThe relevance checker should now allow all questions.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
