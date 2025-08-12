"""
Main RAG Chatbot class that orchestrates UI components with business logic.
"""

import streamlit as st

from src.core.chatbot_logic import ChatbotLogic
from src.ui import ChatManager, MainUIManager, SidebarManager


class RAGChatbot:
    """Main RAG Chatbot application class with UI integration."""

    def __init__(self):
        self.ui_manager = MainUIManager()
        self.sidebar_manager = SidebarManager()
        self.chat_manager = ChatManager()
        self.chatbot_logic = ChatbotLogic()

    def run(self):
        """Main application loop."""
        # Setup UI
        st.set_page_config(page_title="RAG Chatbot - ma_de_001", page_icon="🤖", layout="wide")

        self.ui_manager.render_title()

        # Render sidebar and get configuration
        config = self.sidebar_manager.render_sidebar()

        # Initialize system if needed
        if not self._is_system_initialized():
            if not self._initialize_system(config):
                st.stop()

        # Handle ingestion
        if config["ingest_button"]:
            if not self._handle_ingestion(config):
                st.stop()

        # Display chat history
        self.chat_manager.display_chat_history()

        # Handle user input
        user_question = self.ui_manager.render_chat_input()
        if user_question:
            self._handle_user_question(user_question)

    def _is_system_initialized(self) -> bool:
        """Check if system is properly initialized."""
        status = self.chatbot_logic.get_system_status()
        return all(
            [
                status.get("database_initialized", False),
                status.get("vectorstore_initialized", False),
                status.get("qa_chain_initialized", False),
                # status.get("relevance_checker_initialized", False),  # Disabled
            ]
        )

    def _initialize_system(self, config: dict) -> bool:
        """Initialize the system with configuration."""
        try:
            # Setup database
            if not self.chatbot_logic.setup_database(config["connection_string"], **config["db_params"]):
                self.ui_manager.show_error_message("Không thể chuẩn bị schema PostgreSQL/pgvector")
                return False

            # Load and process documents
            documents = self.chatbot_logic.load_and_process_documents()
            if documents is None:
                self.ui_manager.show_warning_message(
                    "Không có tài liệu để ingest. " "Hãy đảm bảo ba file đầu vào tồn tại trong thư mục hiện tại."
                )
                return False

            # Setup vector store and QA chain if documents exist
            if documents:
                conn_str = config["connection_string"]
                if not conn_str and config["db_params"]:
                    params = config["db_params"]
                    conn_str = (
                        f"postgresql+psycopg://{params['user']}:{params['password']}"
                        f"@{params['host']}:{params['port']}/{params['database']}"
                    )

                # Setup vector store
                if not self.chatbot_logic.setup_vectorstore(conn_str, documents, False):
                    self.ui_manager.show_error_message("Lỗi setup vector store")
                    return False

                # Setup QA chain
                if not self.chatbot_logic.setup_qa_chain():
                    self.ui_manager.show_error_message("Không thể khởi tạo LLM (Gemini). Kiểm tra GEMINI_API_KEY.")
                    return False

            return True
        except Exception as e:
            self.ui_manager.show_error_message(f"Lỗi khởi tạo hệ thống: {e}")
            return False

    def _handle_ingestion(self, config: dict) -> bool:
        """Handle document ingestion."""
        try:
            # Get connection string
            conn_str = config["connection_string"]
            if not conn_str and config["db_params"]:
                params = config["db_params"]
                conn_str = (
                    f"postgresql+psycopg://{params['user']}:{params['password']}"
                    f"@{params['host']}:{params['port']}/{params['database']}"
                )

            # Load documents
            documents = self.chatbot_logic.load_and_process_documents()
            if documents is None:
                return False

            # Setup vector store
            if not self.chatbot_logic.setup_vectorstore(conn_str, documents, config["rebuild"]):
                self.ui_manager.show_error_message("Lỗi ingest dữ liệu")
                return False

            # Setup QA chain
            if not self.chatbot_logic.setup_qa_chain():
                self.ui_manager.show_error_message("Không thể khởi tạo LLM (Gemini). Kiểm tra GEMINI_API_KEY.")
                return False

            self.ui_manager.show_success_message("Ingest hoàn tất!")
            return True
        except Exception as e:
            self.ui_manager.show_error_message(f"Lỗi ingest dữ liệu: {e}")
            return False

    def _handle_user_question(self, question: str):
        """Handle user question processing."""
        try:
            # Process question using logic module
            answer, sources, is_relevant = self.chatbot_logic.process_question(question)

            # Add to chat history
            self.chat_manager.add_user_message(question)
            st.chat_message("user").markdown(question)

            # Handle response
            if not is_relevant:
                self.chat_manager.add_assistant_message(answer)
                st.chat_message("assistant").markdown(answer)
                st.stop()
            else:
                self.chat_manager.add_assistant_message(answer)
                st.chat_message("assistant").markdown(answer)

                # Display sources
                self.chat_manager.display_sources(sources)
        except Exception as e:
            error_msg = f"Lỗi xử lý câu hỏi: {e}"
            self.chat_manager.add_assistant_message(error_msg)
            st.chat_message("assistant").markdown(error_msg)
