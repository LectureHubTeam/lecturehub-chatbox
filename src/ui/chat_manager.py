"""
Chat management and UI interactions.
"""

import json
from typing import Any, List

import streamlit as st

from src.core.config import REFUSAL_MSG


class ChatManager:
    """Manages chat history and UI interactions."""

    def __init__(self):
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state for chat."""
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

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

    def display_sources(self, sources: List[Any]):
        """Display source documents in an expander."""
        if not sources:
            return

        with st.expander("Nguồn tham khảo (chunks)"):
            for i, doc in enumerate(sources, 1):
                meta = json.dumps(doc.metadata, ensure_ascii=False)
                st.markdown(f"- Nguồn {i}: `{meta}`\n\n```\n{doc.page_content[:1000]}\n```\n")

    def handle_irrelevant_question(self, question: str):
        """Handle irrelevant questions by showing refusal message."""
        self.add_user_message(question)
        st.chat_message("user").markdown(question)

        self.add_assistant_message(REFUSAL_MSG)
        st.chat_message("assistant").markdown(REFUSAL_MSG)
        st.stop()

    def process_user_question(self, question: str, qa_chain, relevance_checker):
        """
        Process a user question through the QA chain.

        Args:
            question: User question
            qa_chain: QA chain instance
            relevance_checker: Relevance checker instance
        """
        self.add_user_message(question)
        st.chat_message("user").markdown(question)

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

        self.add_assistant_message(answer)
        st.chat_message("assistant").markdown(answer)

        # Display sources
        self.display_sources(sources)
