#!/usr/bin/env python3
"""
Test QA chain initialization.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_qa_chain_initialization():
    """Test QA chain initialization."""
    print("Testing QA Chain Initialization")
    print("=" * 40)

    try:
        from src.core.chatbot_logic import ChatbotLogic

        # Create chatbot
        chatbot = ChatbotLogic()

        # Test system status before initialization
        print("1. System status before initialization:")
        status = chatbot.get_system_status()
        for key, value in status.items():
            print(f"   {key}: {value}")

        # Test QA chain initialization without proper setup
        print("\n2. Testing QA chain setup without vectorstore:")
        success = chatbot.setup_qa_chain()
        print(f"   QA chain setup: {'✅ Success' if success else '❌ Failed'}")

        # Test with mock documents
        print("\n3. Testing with mock setup:")

        # Setup memory
        chatbot.setup_memory("buffer_window", 5)

        # Create a proper mock retriever
        from langchain_core.documents import Document
        from langchain_core.retrievers import BaseRetriever

        class MockRetriever(BaseRetriever):
            def _get_relevant_documents(self, query):
                return [Document(page_content="Mock document content", metadata={"source": "mock"})]

            async def _aget_relevant_documents(self, query):
                return self._get_relevant_documents(query)

        class MockVectorStore:
            def __init__(self):
                pass

        class MockVectorStoreManager:
            def build_retriever(self, vectorstore, problem_id):
                return MockRetriever()

        chatbot._vectorstore = MockVectorStore()
        chatbot.vectorstore_manager = MockVectorStoreManager()

        # Test QA chain setup
        success = chatbot.setup_qa_chain()
        print(f"   QA chain setup with mock: {'✅ Success' if success else '❌ Failed'}")

        # Test system status after initialization
        print("\n4. System status after initialization:")
        status = chatbot.get_system_status()
        for key, value in status.items():
            print(f"   {key}: {value}")

        # Test question processing
        print("\n5. Testing question processing:")
        answer, sources, is_relevant = chatbot.process_question("Test question")
        print(f"   Answer: {answer[:50]}...")
        print(f"   Is relevant: {is_relevant}")

        print("\n✅ QA chain initialization test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_qa_chain_initialization()
