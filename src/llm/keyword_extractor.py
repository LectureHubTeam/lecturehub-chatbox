"""
Keyword extraction and relevance checking functionality.
"""

import re
from typing import Any, List, Set

from src.core.config import DEFAULT_MAX_KEYWORDS, PROBLEM_ID


class KeywordExtractor:
    """Extracts keywords from documents for relevance checking."""

    def __init__(self, max_keywords: int = DEFAULT_MAX_KEYWORDS):
        self.max_keywords = max_keywords
        self.stopwords = self._get_stopwords()

    def extract_keywords(self, docs: List[Any]) -> Set[str]:
        """
        Extract keywords from documents.

        Args:
            docs: List of document objects

        Returns:
            Set of keyword strings
        """
        text = "\n".join([d.page_content for d in docs])
        tokens = re.findall(r"[\w\-À-ỹ]{3,}", text, flags=re.UNICODE)

        freq = {}
        for token in tokens:
            token_lower = token.lower()
            freq[token_lower] = freq.get(token_lower, 0) + 1

        # Keep top N non-stop tokens
        sorted_tokens = sorted((k for k in freq.keys() if k not in self.stopwords), key=lambda k: -freq[k])

        keywords = set(sorted_tokens[: self.max_keywords])

        # Add problem-specific anchors
        keywords.update({"bài", "giảng", "đề", "bài", "code", "python", PROBLEM_ID, "pdf", "md"})

        return keywords

    def _get_stopwords(self) -> Set[str]:
        """Get Vietnamese and English stopwords."""
        # TODO: update later
        return set(
            """
            ...
            """.split()
        )


class RelevanceChecker:
    """Checks if a question is relevant to the documents."""

    def __init__(self, keywords: Set[str]):
        self.keywords = keywords

    def is_relevant(self, question: str) -> bool:
        """
        Check if question is relevant based on keywords.

        Args:
            question: User question string

        Returns:
            True if question is relevant, False otherwise
        """
        # Always return True for now to allow all questions
        # This can be made more sophisticated later
        return True

        # Original strict checking (commented out)
        # question_lower = question.lower()
        # return any(keyword in question_lower for keyword in self.keywords)
