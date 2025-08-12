"""
Test file demonstrating how to test individual components.

This file shows how the refactored architecture makes it easy to test
individual components in isolation.
"""

import os

# Test imports
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.config import PROBLEM_ID, REQUIRED_FILES
from src.database.database import DatabaseManager
from src.llm.keyword_extractor import KeywordExtractor, RelevanceChecker
from src.utils.document_loader import DocumentLoader, DocumentProcessor


def test_config():
    """Test configuration constants."""
    print("Testing configuration...")
    assert PROBLEM_ID == "ma_de_001"
    assert "pdf" in REQUIRED_FILES
    assert "markdown" in REQUIRED_FILES
    assert "python" in REQUIRED_FILES
    print("✓ Configuration test passed")


def test_document_loader():
    """Test document loader component."""
    print("Testing document loader...")

    loader = DocumentLoader()
    assert hasattr(loader, "supported_file_types")
    assert "pdf" in loader.supported_file_types
    assert "markdown" in loader.supported_file_types
    assert "python" in loader.supported_file_types

    # Test loading (will return empty list if files don't exist)
    docs = loader.load_all_documents()
    assert isinstance(docs, list)
    print("✓ Document loader test passed")


def test_document_processor():
    """Test document processor component."""
    print("Testing document processor...")

    processor = DocumentProcessor()
    assert hasattr(processor, "chunk_size")
    assert hasattr(processor, "chunk_overlap")
    assert hasattr(processor, "splitter")

    # Test with empty documents
    empty_docs = []
    result = processor.chunk_documents(empty_docs)
    assert isinstance(result, list)
    print("✓ Document processor test passed")


def test_keyword_extractor():
    """Test keyword extractor component."""
    print("Testing keyword extractor...")

    extractor = KeywordExtractor()
    assert hasattr(extractor, "max_keywords")
    assert hasattr(extractor, "stopwords")

    # Test with empty documents
    empty_docs = []
    keywords = extractor.extract_keywords(empty_docs)
    assert isinstance(keywords, set)
    assert PROBLEM_ID in keywords  # Should include problem ID
    print("✓ Keyword extractor test passed")


def test_relevance_checker():
    """Test relevance checker component."""
    print("Testing relevance checker...")

    keywords = {"bài", "giảng", "code", PROBLEM_ID}
    checker = RelevanceChecker(keywords)

    # Test relevant question
    relevant_q = "Giải thích bài giảng này"
    assert checker.is_relevant(relevant_q)

    # Test irrelevant question
    irrelevant_q = "Thời tiết hôm nay thế nào"
    assert not checker.is_relevant(irrelevant_q)
    print("✓ Relevance checker test passed")


def test_database_manager():
    """Test database manager component."""
    print("Testing database manager...")

    # Test with mock connection string
    conn_str = "postgresql+psycopg://test:test@localhost:5432/test"
    db_manager = DatabaseManager(conn_str)

    assert db_manager.connection_string == conn_str
    assert db_manager._psycopg_conn_str == "postgresql://test:test@localhost:5432/test"
    print("✓ Database manager test passed")


def run_all_tests():
    """Run all component tests."""
    print("Running component tests...\n")

    test_config()
    test_document_loader()
    test_document_processor()
    test_keyword_extractor()
    test_relevance_checker()
    test_database_manager()

    print("\n✓ All component tests passed!")


if __name__ == "__main__":
    run_all_tests()
