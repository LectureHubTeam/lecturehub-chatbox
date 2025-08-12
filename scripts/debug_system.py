#!/usr/bin/env python3
"""
Debug script to check system status and identify issues.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def debug_system_status():
    """Debug system status."""
    print("🔍 Debugging System Status")
    print("=" * 50)

    try:
        from src.core.chatbot_logic import create_chatbot

        # Create chatbot
        chatbot = create_chatbot()
        print("✅ Chatbot created")

        # Check initial status
        status = chatbot.get_system_status()
        print("\nInitial Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Test each component
        print("\n🔍 Testing Components:")

        # Test database setup
        print("  Testing database setup...")
        db_result = chatbot.setup_database(
            host="localhost", port="5432", database="embedding", user="root", password="root_password"
        )
        print(f"    Database setup: {db_result}")

        # Test document loading
        print("  Testing document loading...")
        documents = chatbot.load_and_process_documents()
        if documents is None:
            print("    No documents found")
        else:
            print(f"    Loaded {len(documents)} documents")

        # Check status after document loading
        status = chatbot.get_system_status()
        print("\nStatus after document loading:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Test vector store setup (if documents exist)
        if documents:
            print("  Testing vector store setup...")
            conn_str = "postgresql+psycopg://root:root_password@localhost:5432/embedding"
            vs_result = chatbot.setup_vectorstore(conn_str, documents, False)
            print(f"    Vector store setup: {vs_result}")

            # Test QA chain setup
            if vs_result:
                print("  Testing QA chain setup...")
                qa_result = chatbot.setup_qa_chain()
                print(f"    QA chain setup: {qa_result}")

        # Final status
        status = chatbot.get_system_status()
        print("\nFinal Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Test question processing
        print("\n🔍 Testing Question Processing:")
        answer, sources, is_relevant = chatbot.process_question("Test question")
        print(f"  Answer: {answer}")
        print(f"  Is relevant: {is_relevant}")
        print(f"  Sources count: {len(sources)}")

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main debug function."""
    print("🔧 LectureHub Chatbot - System Debug")
    print("=" * 50)

    if debug_system_status():
        print("\n🎉 Debug completed successfully!")
        print("\nCheck the status above to identify any issues.")
    else:
        print("\n❌ Debug failed!")
        print("Please check the error messages above.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
