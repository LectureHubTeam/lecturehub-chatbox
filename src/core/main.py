"""
Main entry point for the RAG Chatbot application.

This is the refactored version of the original app.py, now using a modular,
class-based architecture for better maintainability and organization.

Usage:
    $ streamlit run main.py
"""

from src.core.rag_chatbot import RAGChatbot


def main():
    """Main application entry point."""
    chatbot = RAGChatbot()
    chatbot.run()


if __name__ == "__main__":
    main()
