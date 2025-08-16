"""
UI components for configuration and sidebar.
"""

import os

import streamlit as st

from src.core.config import DEFAULT_CONN_STR, get_available_problems


class SidebarManager:
    """Manages the sidebar configuration UI."""

    def __init__(self):
        pass

    def render_sidebar(self):
        """Render the sidebar configuration."""
        with st.sidebar:
            st.header("Cấu hình")

            # Problem selection section
            st.subheader("Problem Selection")

            # Get available problems
            available_problems = get_available_problems()

            if not available_problems:
                st.error("Không tìm thấy problem nào trong thư mục data/lectures/")
                st.info("Hãy tạo thư mục problem với các file .pdf, .md, .py")
                # Return default config instead of None
                return {
                    "selected_problem": None,
                    "connection_string": DEFAULT_CONN_STR,
                    "db_params": {},
                    "memory_type": "buffer_window",
                    "memory_k": 5,
                    "rebuild": False,
                    "ingest_button": False,
                }

            # Problem selection
            selected_problem = st.selectbox(
                "Chọn Problem", options=available_problems, index=0, help="Chọn problem để chat"
            )

            # Show problem files
            if selected_problem:
                st.info(f"📁 Problem: {selected_problem}")

                # Show files in the problem folder
                problem_files = []
                problem_dir = os.path.join("data/lectures", selected_problem)
                if os.path.exists(problem_dir):
                    for file in os.listdir(problem_dir):
                        if file.endswith((".pdf", ".md", ".py")):
                            problem_files.append(file)

                if problem_files:
                    st.write("📄 Files:")
                    for file in problem_files:
                        st.write(f"  • {file}")
                else:
                    st.warning("Không tìm thấy file nào trong thư mục problem")

            # Use default memory settings
            memory_type = "buffer_window"
            memory_k = 5
            rebuild = False

            # Only show ingest button if no data exists
            ingest_btn = st.button("Ingest dữ liệu (nếu cần)")

            return {
                "selected_problem": selected_problem,
                "connection_string": DEFAULT_CONN_STR,
                "db_params": {},
                "memory_type": memory_type,
                "memory_k": memory_k,
                "rebuild": rebuild,
                "ingest_button": ingest_btn,
            }


class MainUIManager:
    """Manages the main UI components."""

    def __init__(self):
        pass

    def render_title(self, problem_name: str = None):
        """Render the main title."""
        if problem_name:
            st.title(f"🤖 RAG Chatbot — {problem_name}")
        else:
            st.title("🤖 RAG Chatbot")

    def render_chat_input(self):
        """Render the chat input."""
        # Add some spacing before chat input
        st.write("")  # Add empty line for spacing
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
