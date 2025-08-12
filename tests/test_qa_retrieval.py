#!/usr/bin/env python3
"""
Test script to check QA retrieval and relevance issues.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_qa_retrieval():
    """Test QA retrieval with various questions."""
    print("Testing QA Retrieval")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import ChatbotLogic
        from src.core.config import DEFAULT_CONN_STR

        # Create chatbot logic
        chatbot = ChatbotLogic()
        print("✅ Chatbot logic created")

        # Setup database
        if not chatbot.setup_database():
            print("❌ Database setup failed")
            return False
        print("✅ Database setup completed")

        # Load and process documents
        documents = chatbot.load_and_process_documents()
        if documents is None:
            print("❌ Document loading failed")
            return False
        print(f"✅ Loaded {len(documents)} documents")

        # Setup vector store
        if not chatbot.setup_vectorstore(DEFAULT_CONN_STR, documents):
            print("❌ Vector store setup failed")
            return False
        print("✅ Vector store setup completed")

        # Setup QA chain
        if not chatbot.setup_qa_chain():
            print("❌ QA chain setup failed")
            return False
        print("✅ QA chain setup completed")

        # Test various questions
        test_questions = [
            "sample input của đề là gì",
            "Tên đề à gì",
            "Giải thích input, output mà đề yêu cầu",
            "Thuật toán Caesar là gì?",
            "Cách giải mã Caesar cipher?",
            "Input và output của bài toán?",
            "Mô tả bài toán",
            "Cách xử lý chữ cái thường và in hoa?",
            "Time complexity của thuật toán?",
            "Space complexity của thuật toán?",
            "Cách sử dụng hàm ord() và chr()?",
            "Ví dụ về phép modulo trong giải mã?",
        ]

        print("\nTesting questions:")
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")

            # Process question
            answer, sources, is_relevant = chatbot.process_question(question)

            print(f"   Answer: {answer[:200]}...")
            print(f"   Sources count: {len(sources)}")
            print(f"   Is relevant: {is_relevant}")

            # Check if answer is refusal message
            refusal_msg = "Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi."
            if refusal_msg in answer:
                print("   ❌ Getting refusal message!")
            else:
                print("   ✅ Not getting refusal message")

            # Show first source if available
            if sources:
                print(f"   First source: {sources[0].page_content[:100]}...")
            else:
                print("   No sources found")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_qa_retrieval()
