"""
Memory management for chatbot conversations.
"""

from typing import Any, Dict, List

import streamlit as st
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain_core.messages import get_buffer_string

# from src.utils.logger import logger


class ChatMemoryManager:
    """Manages conversation memory for the chatbot."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of ChatMemoryManager exists."""
        if cls._instance is None:
            cls._instance = super(ChatMemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, memory_type: str = "buffer_window", max_tokens: int = 2000, k: int = 5):
        """
        Initialize memory manager. Only initializes once, subsequent calls return the existing instance.

        Args:
            memory_type: Type of memory ("buffer_window", "summary", "hybrid")
            max_tokens: Maximum tokens for summary memory
            k: Number of messages to keep in buffer window
        """
        # Only initialize once
        if self._initialized:
            return

        self.memory_type = memory_type
        self.max_tokens = max_tokens
        self.k = k
        self.memory = None
        self._initialize_memory()

        self._initialized = True

    def _initialize_memory(self):
        """Initialize the appropriate memory type."""
        if self.memory_type == "buffer_window":
            self.memory = ConversationBufferWindowMemory(
                k=self.k, return_messages=True, memory_key="chat_history", input_key="question", output_key="answer"
            )
        elif self.memory_type == "summary":
            self.memory = ConversationSummaryMemory(
                llm=None,  # Will be set later
                max_token_limit=self.max_tokens,
                return_messages=True,
                memory_key="chat_history",
                input_key="question",
                output_key="answer",
            )
        elif self.memory_type == "hybrid":
            # Use both buffer window and summary
            self.memory = ConversationBufferWindowMemory(
                k=self.k, return_messages=True, memory_key="chat_history", input_key="query"
            )
            self.summary_memory = ConversationSummaryMemory(
                llm=None,
                max_token_limit=self.max_tokens,
                return_messages=True,
                memory_key="summary",
                input_key="question",
                output_key="answer",
            )
        else:
            raise ValueError(f"Unsupported memory type: {self.memory_type}")

    def add_user_message(self, message: str):
        """Add a user message to memory."""
        try:
            if self.memory_type == "hybrid":
                self.memory.chat_memory.add_user_message(message)
                self.summary_memory.chat_memory.add_user_message(message)
            else:
                self.memory.chat_memory.add_user_message(message)
        except Exception as e:
            print(f"ERROR: Error adding user message to memory: {e}")

    def add_ai_message(self, message: str):
        """Add an AI message to memory."""
        try:
            if self.memory_type == "hybrid":
                self.memory.chat_memory.add_ai_message(message)
                self.summary_memory.chat_memory.add_ai_message(message)
            else:
                self.memory.chat_memory.add_ai_message(message)
        except Exception as e:
            print(f"ERROR: Error adding AI message to memory: {e}")

    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for the chain."""
        try:
            if self.memory_type == "hybrid":
                buffer_vars = self.memory.load_memory_variables({})
                summary_vars = self.summary_memory.load_memory_variables({})
                return {"chat_history": buffer_vars.get("chat_history", []), "summary": summary_vars.get("summary", "")}
            else:
                return self.memory.load_memory_variables({})
        except Exception as e:
            print(f"ERROR: Error loading memory variables: {e}")
            return {"chat_history": []}

    def get_chat_history_string(self) -> str:
        """Get chat history as a formatted string."""
        try:
            if self.memory_type == "hybrid":
                buffer_vars = self.memory.load_memory_variables({})
                summary_vars = self.summary_memory.load_memory_variables({})

                chat_history = buffer_vars.get("chat_history", [])
                summary = summary_vars.get("summary", "")

                if summary:
                    return (
                        f"Tóm tắt cuộc hội thoại trước: {summary}\n\n"
                        f"Lịch sử gần đây:\n{get_buffer_string(chat_history)}"
                    )
                else:
                    return get_buffer_string(chat_history)
            else:
                vars = self.memory.load_memory_variables({})
                chat_history = vars.get("chat_history", [])
                return get_buffer_string(chat_history)
        except Exception as e:
            print(f"ERROR: Error getting chat history string: {e}")
            return ""

    def clear_memory(self):
        """Clear all memory."""
        try:
            if self.memory_type == "hybrid":
                self.memory.clear()
                self.summary_memory.clear()
            else:
                self.memory.clear()
        except Exception as e:
            print(f"ERROR: Error clearing memory: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        try:
            if self.memory_type == "hybrid":
                buffer_vars = self.memory.load_memory_variables({})
                summary_vars = self.summary_memory.load_memory_variables({})

                buffer_messages = buffer_vars.get("chat_history", [])
                summary = summary_vars.get("summary", "")

                return {
                    "memory_type": self.memory_type,
                    "buffer_messages_count": len(buffer_messages),
                    "has_summary": bool(summary),
                    "summary_length": len(summary) if summary else 0,
                }
            else:
                vars = self.memory.load_memory_variables({})
                chat_history = vars.get("chat_history", [])

                return {
                    "memory_type": self.memory_type,
                    "messages_count": len(chat_history),
                    "max_messages": self.k if self.memory_type == "buffer_window" else "unlimited",
                }
        except Exception as e:
            print(f"ERROR: Error getting memory stats: {e}")
            return {"error": str(e)}


class StreamlitMemoryManager:
    """Memory manager that integrates with Streamlit session state."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of StreamlitMemoryManager exists."""
        if cls._instance is None:
            cls._instance = super(StreamlitMemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, memory_type: str = "buffer_window", k: int = 10):
        """
        Initialize Streamlit memory manager. Only initializes once, subsequent calls return the existing instance.

        Args:
            memory_type: Type of memory ("buffer_window", "persistent")
            k: Number of messages to keep in buffer
        """
        # Only initialize once
        if self._initialized:
            return

        self.memory_type = memory_type
        self.k = k
        self._initialize_session_state()

        self._initialized = True

    def _initialize_session_state(self):
        """Initialize Streamlit session state for memory."""
        if "chat_memory" not in st.session_state:
            st.session_state["chat_memory"] = []

        if "memory_stats" not in st.session_state:
            st.session_state["memory_stats"] = {"total_messages": 0, "user_messages": 0, "ai_messages": 0}

    def add_user_message(self, message: str):
        """Add a user message to memory."""
        st.session_state["chat_memory"].append(
            {"role": "user", "content": message, "timestamp": st.session_state.get("current_timestamp", 0)}
        )

        # Update stats
        st.session_state["memory_stats"]["total_messages"] += 1
        st.session_state["memory_stats"]["user_messages"] += 1

        # Maintain buffer size
        if self.memory_type == "buffer_window" and len(st.session_state["chat_memory"]) > self.k * 2:
            st.session_state["chat_memory"] = st.session_state["chat_memory"][-self.k * 2 :]

    def add_ai_message(self, message: str):
        """Add an AI message to memory."""
        st.session_state["chat_memory"].append(
            {"role": "assistant", "content": message, "timestamp": st.session_state.get("current_timestamp", 0)}
        )

        # Update stats
        st.session_state["memory_stats"]["total_messages"] += 1
        st.session_state["memory_stats"]["ai_messages"] += 1

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history."""
        return st.session_state.get("chat_memory", [])

    def get_chat_history_string(self) -> str:
        """Get chat history as a formatted string."""
        history = self.get_chat_history()
        if not history:
            return ""

        formatted_history = []
        for msg in history:
            role = "Người dùng" if msg["role"] == "user" else "Trợ lý"
            formatted_history.append(f"{role}: {msg['content']}")

        return "\n".join(formatted_history)

    def clear_memory(self):
        """Clear all memory."""
        st.session_state["chat_memory"] = []
        st.session_state["memory_stats"] = {"total_messages": 0, "user_messages": 0, "ai_messages": 0}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return st.session_state.get("memory_stats", {})

    def get_recent_context(self, num_messages: int = 5) -> str:
        """Get recent conversation context for LLM."""
        history = self.get_chat_history()
        if not history:
            return ""

        recent = history[-num_messages * 2 :]  # Get last N exchanges
        context_parts = []

        for msg in recent:
            role = "Human" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)
