"""
UI components for configuration and sidebar.
"""

import os

import streamlit as st

from src.core.config import DEFAULT_CONN_STR


class SidebarManager:
    """Manages the sidebar configuration UI."""

    def __init__(self):
        pass

    def render_sidebar(self):
        """Render the sidebar configuration."""
        with st.sidebar:
            st.header("Cấu hình")

            # Database configuration section
            st.subheader("Database Configuration")

            use_connection_string = st.checkbox(
                "Use connection string",
                value=False,
                help="Check to use full connection string instead of individual parameters",
            )

            if use_connection_string:
                conn_str = st.text_input(
                    "PostgreSQL + pgvector connection string",
                    value=DEFAULT_CONN_STR,
                    help="Ví dụ: postgresql+psycopg://user:pass@host:5432/db",
                )
                db_params = {}
            else:
                # Individual database parameters
                col1, col2 = st.columns(2)
                with col1:
                    db_host = st.text_input("Host", value=os.getenv("DB_HOST", "localhost"))
                    db_port = st.text_input("Port", value=os.getenv("DB_PORT", "5432"))
                    db_name = st.text_input("Database", value=os.getenv("DB_NAME", "embedding"))
                with col2:
                    db_user = st.text_input("User", value=os.getenv("DB_USER", "root"))
                    db_password = st.text_input(
                        "Password", value=os.getenv("DB_PASSWORD", "root_password"), type="password"
                    )

                conn_str = None
                db_params = {
                    "host": db_host,
                    "port": db_port,
                    "database": db_name,
                    "user": db_user,
                    "password": db_password,
                }

            # LLM configuration section
            st.subheader("LLM Configuration")
            api_key = st.text_input(
                "GEMINI_API_KEY",
                value=os.environ.get("GEMINI_API_KEY", ""),
                type="password",
                help="Yêu cầu cho Gemini LLM (miễn phí).",
            )

            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key

            # Memory configuration section
            st.subheader("Memory Configuration")
            memory_type = st.selectbox(
                "Memory Type",
                options=["buffer_window", "summary", "hybrid"],
                index=0,
                help="Loại memory để lưu trữ lịch sử hội thoại",
            )
            memory_k = st.slider(
                "Buffer Size (k)",
                min_value=1,
                max_value=20,
                value=5,
                help="Số lượng tin nhắn gần nhất để giữ trong buffer",
            )

            # Application configuration section
            st.subheader("Application Configuration")
            rebuild = st.checkbox("Tái tạo (rebuild) chỉ mục/collection", value=False)

            ingest_btn = st.button("Ingest dữ liệu")

            return {
                "connection_string": conn_str,
                "db_params": db_params,
                "api_key": api_key,
                "memory_type": memory_type,
                "memory_k": memory_k,
                "rebuild": rebuild,
                "ingest_button": ingest_btn,
            }


class MainUIManager:
    """Manages the main UI components."""

    def __init__(self):
        pass

    def render_title(self):
        """Render the main title."""
        st.title("🤖 RAG Chatbot — Bài giảng (ma_de_001)")

    def render_chat_input(self):
        """Render the chat input."""
        return st.chat_input("Đặt câu hỏi về bài giảng/đề/code...")

    def show_info_message(self, message: str):
        """Show an info message."""
        st.info(message)

    def show_warning_message(self, message: str):
        """Show a warning message."""
        st.warning(message)

    def show_error_message(self, message: str):
        """Show an error message."""
        st.error(message)

    def show_success_message(self, message: str):
        """Show a success message."""
        st.success(message)

    def show_loading_spinner(self, message: str):
        """Show a loading spinner."""
        return st.spinner(message)
