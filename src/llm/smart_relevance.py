"""
Smart relevance checking functionality.
"""

from typing import Set

from src.core.config import PROBLEM_ID


class SmartRelevanceChecker:
    """Smart relevance checker that's more flexible than strict keyword matching."""

    def __init__(self, keywords: Set[str]):
        self.keywords = keywords
        self.general_question_words = {
            "what",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
            "explain",
            "describe",
            "tell",
            "show",
            "help",
            "understand",
            "learn",
            "know",
            "là gì",
            "như thế nào",
            "tại sao",
            "khi nào",
            "ở đâu",
            "ai",
            "giải thích",
            "mô tả",
            "cho biết",
            "hiển thị",
            "giúp",
            "hiểu",
            "học",
            "biết",
        }

    def is_relevant(self, question: str) -> bool:
        """
        Check if question is relevant using smart heuristics.

        Args:
            question: User question string

        Returns:
            True if question is relevant, False otherwise
        """
        question_lower = question.lower().strip()

        # If question is too short, it's probably not relevant
        if len(question_lower) < 3:
            return False

        # If question contains obvious off-topic words, reject it
        off_topic_words = {
            "weather",
            "time",
            "date",
            "news",
            "sports",
            "music",
            "movie",
            "thời tiết",
            "thời gian",
            "ngày",
            "tin tức",
            "thể thao",
            "âm nhạc",
            "phim",
        }

        if any(word in question_lower for word in off_topic_words):
            return False

        # If question contains general question words or seems like a learning question, accept it
        if any(word in question_lower for word in self.general_question_words):
            return True

        # If question contains any keywords from documents, accept it
        if any(keyword in question_lower for keyword in self.keywords):
            return True

        # If question is about the problem ID, accept it
        if PROBLEM_ID.lower() in question_lower:
            return True

        # If question seems like it's asking for help or explanation, accept it
        help_words = {"help", "giúp", "assist", "hỗ trợ", "explain", "giải thích"}
        if any(word in question_lower for word in help_words):
            return True

        # Default: accept the question (more permissive)
        return True


class StrictRelevanceChecker:
    """Strict relevance checker that requires keyword matching."""

    def __init__(self, keywords: Set[str]):
        self.keywords = keywords

    def is_relevant(self, question: str) -> bool:
        """
        Check if question is relevant based on strict keyword matching.

        Args:
            question: User question string

        Returns:
            True if question is relevant, False otherwise
        """
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in self.keywords)


class PermissiveRelevanceChecker:
    """Permissive relevance checker that accepts most questions."""

    def __init__(self, keywords: Set[str]):
        self.keywords = keywords

    def is_relevant(self, question: str) -> bool:
        """
        Check if question is relevant (always returns True).

        Args:
            question: User question string

        Returns:
            True (always accepts questions)
        """
        return True
