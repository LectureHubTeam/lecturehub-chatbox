"""
Chat management and UI interactions.
"""

import json
from typing import Any, List

import streamlit as st

from src.core.config import REFUSAL_MSG
from src.memory import StreamlitMemoryManager


class ChatManager:
    """Manages chat history and UI interactions."""

    def __init__(self):
        self.memory_manager = StreamlitMemoryManager()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state for chat."""
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        if "current_question" not in st.session_state:
            st.session_state["current_question"] = None
        if "current_sources" not in st.session_state:
            st.session_state["current_sources"] = []

    def _is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting."""
        greetings = [
            "hi",
            "hello",
            "xin chào",
            "chào",
            "hey",
            "chào bạn",
            "hi bạn",
            "hello bạn",
            "chào em",
            "hi em",
            "hello em",
            "chào anh",
            "hi anh",
            "hello anh",
            "chào chị",
            "hi chị",
            "hello chị",
            "chào thầy",
            "chào cô",
            "chào giáo viên",
        ]
        return message.lower().strip() in greetings

    def _is_simple_question(self, message: str) -> bool:
        """Check if the message is a simple question that doesn't need detailed RAG."""
        simple_patterns = [
            "bạn có khỏe không",
            "bạn thế nào",
            "khỏe không",
            "thế nào",
            "cảm ơn",
            "thanks",
            "thank you",
            "tạm biệt",
            "goodbye",
            "bye",
            "ok",
            "okay",
            "được",
            "tốt",
            "hay",
            "giỏi",
            "tuyệt",
        ]
        return any(pattern in message.lower() for pattern in simple_patterns)

    def add_user_message(self, message: str):
        """Add a user message to chat history."""
        st.session_state["messages"].append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        """Add an assistant message to chat history."""
        st.session_state["messages"].append({"role": "assistant", "content": message})

    def display_chat_history(self):
        """Display the chat history in the UI."""
        for msg in st.session_state["messages"]:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["content"])
            else:
                st.chat_message("assistant").markdown(msg["content"])

        # Display sources if available
        if st.session_state.get("current_sources"):
            self.display_sources_from_session()

    def display_sources(self, sources: List[Any]):
        """Display source documents in an expander."""
        if not sources:
            return

        # Store sources in session state for persistence
        st.session_state["current_sources"] = sources

        with st.expander("Nguồn tham khảo (chunks)", expanded=False):
            for i, doc in enumerate(sources, 1):
                meta = json.dumps(doc.metadata, ensure_ascii=False)
                st.markdown(f"**Nguồn {i}:**")
                st.markdown("*Metadata:* `{}`".format(meta))
                st.markdown("*Nội dung:*")
                st.code(doc.page_content[:1000], language="text")
                st.markdown("---")

    def handle_irrelevant_question(self, question: str):
        """Handle irrelevant questions by showing refusal message."""
        self.add_user_message(question)
        self.add_assistant_message(REFUSAL_MSG)
        st.stop()

    def handle_greeting(self, greeting: str):
        """Handle greetings with short, friendly responses."""
        self.add_user_message(greeting)

        responses = [
            "Xin chào! 😊 Tôi là trợ lý AI hỗ trợ học tập về bài toán tin." "Bạn có câu hỏi gì về bài giảng không?",
            "Chào bạn! 👋 Tôi sẵn sàng giúp bạn học về toán tin. Hãy hỏi bất cứ điều gì!",
            "Hi! 😄 Tôi ở đây để hỗ trợ bạn học tập. Bạn muốn tìm hiểu gì về bài toán này?",
            "Xin chào! 🌟 Tôi là chatbot hỗ trợ học tập. Bạn có thắc mắc gì về toán tin không?",
        ]

        import random

        response = random.choice(responses)
        self.add_assistant_message(response)

    def handle_simple_question(self, question: str):
        """Handle simple questions with short responses."""
        self.add_user_message(question)

        if "cảm ơn" in question.lower() or "thanks" in question.lower():
            response = "Rất vui được giúp bạn! 😊 Nếu có thêm câu hỏi gì, đừng ngại hỏi nhé!"
        elif "tạm biệt" in question.lower() or "goodbye" in question.lower() or "bye" in question.lower():
            response = "Tạm biệt! 👋 Chúc bạn học tập tốt! Hẹn gặp lại!"
        elif "khỏe" in question.lower() or "thế nào" in question.lower():
            response = "Cảm ơn bạn! 😊 Tôi luôn sẵn sàng hỗ trợ học tập. Bạn có câu hỏi gì về Caesar Cipher không?"
        else:
            response = "Cảm ơn bạn! 😊 Tôi luôn sẵn sàng hỗ trợ. Bạn có câu hỏi gì về bài giảng không?"

        self.add_assistant_message(response)

    def process_user_question(self, question: str, qa_chain, relevance_checker):
        """
        Process a user question through the QA chain.

        Args:
            question: User question
            qa_chain: QA chain instance
            relevance_checker: Relevance checker instance
        """
        # Pre-processing: Handle greetings and simple questions
        if self._is_greeting(question):
            self.handle_greeting(question)
            return

        if self._is_simple_question(question):
            self.handle_simple_question(question)
            return

        # Add user message to history
        self.add_user_message(question)

        # Relevance checking disabled - always process questions
        # if not relevance_checker.is_relevant(question):
        #     self.handle_irrelevant_question(question)
        #     return

        # Process with QA chain
        with st.spinner("Đang truy vấn tài liệu..."):
            try:
                result = qa_chain.invoke({"query": question})
                answer = result.get("result", "")
                sources = result.get("source_documents", [])
            except Exception as e:
                answer = f"Đã xảy ra lỗi khi gọi LLM/RAG: {e}"
                sources = []

        # Handle empty answer
        if not answer.strip():
            answer = REFUSAL_MSG

        # Add assistant message to history
        self.add_assistant_message(answer)

        # Display sources
        self.display_sources(sources)

    def display_sources_from_session(self):
        """Display source documents from session state."""
        sources = st.session_state.get("current_sources", [])
        if not sources:
            return

        with st.expander("Nguồn tham khảo (chunks)", expanded=False):
            for i, doc in enumerate(sources, 1):
                meta = json.dumps(doc.metadata, ensure_ascii=False)
                st.markdown(f"**Nguồn {i}:**")
                st.markdown("*Metadata:* `{}`".format(meta))
                st.markdown("*Nội dung:*")
                st.code(doc.page_content[:1000], language="text")
                st.markdown("---")

    def display_memory_stats(self):
        """Display memory statistics in the sidebar."""
        stats = self.memory_manager.get_memory_stats()

        with st.sidebar.expander("📊 Thống kê Memory", expanded=False):
            st.write(f"**Tổng số tin nhắn:** {stats.get('total_messages', 0)}")
            st.write(f"**Tin nhắn người dùng:** {stats.get('user_messages', 0)}")
            st.write(f"**Tin nhắn AI:** {stats.get('ai_messages', 0)}")

            if st.button("🗑️ Xóa Memory", type="secondary"):
                self.clear_memory()
                st.rerun()

    def clear_memory(self):
        """Clear all memory and chat history."""
        self.memory_manager.clear_memory()
        st.session_state["messages"] = []
        st.session_state["current_sources"] = []
        st.session_state["current_question"] = None
        st.success("✅ Đã xóa memory và lịch sử chat!")

    def get_recent_context(self, num_messages: int = 5) -> str:
        """Get recent conversation context for LLM."""
        return self.memory_manager.get_recent_context(num_messages)

    def process_new_question(self, question: str, qa_chain, relevance_checker):
        """
        Process a new question, avoiding duplicates.

        Args:
            question: User question
            qa_chain: QA chain instance
            relevance_checker: Relevance checker instance
        """
        # Check if this is a new question
        if question == st.session_state.get("current_question"):
            return  # Skip if same question

        # Update current question
        st.session_state["current_question"] = question

        # Process the question
        self.process_user_question(question, qa_chain, relevance_checker)
