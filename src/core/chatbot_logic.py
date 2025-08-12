"""
Core chatbot logic separated from Streamlit UI.

This module contains all the business logic that can be tested independently
without requiring Streamlit context.
"""

from typing import Any, Dict, List, Optional, Tuple

from src.core.config import COLLECTION_NAME, PROBLEM_ID, REFUSAL_MSG
from src.database import DatabaseManager, VectorStoreManager
from src.llm import KeywordExtractor, LLMChainBuilder
from src.llm.smart_relevance import SmartRelevanceChecker
from src.utils import DocumentLoader, DocumentProcessor
from src.utils.logger import logger


class ChatbotLogic:
    """Core chatbot logic without Streamlit dependencies."""

    def __init__(self):
        self.document_loader = DocumentLoader()
        self.document_processor = DocumentProcessor()
        self.keyword_extractor = KeywordExtractor()
        self.llm_builder = LLMChainBuilder()

        # State variables
        self.vectorstore_manager = None
        self.relevance_checker = None
        self.qa_chain = None
        self.database_manager = None

    def setup_database(self, connection_string: str = None, **db_params) -> bool:
        """
        Setup database connection and schema.

        Args:
            connection_string: Database connection string
            **db_params: Individual database parameters

        Returns:
            True if setup successful, False otherwise
        """
        try:
            self.database_manager = DatabaseManager(connection_string, **db_params)
            self.database_manager.ensure_pgvector_schema()
            logger.info("Database setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False

    def load_and_process_documents(self) -> Optional[List[Any]]:
        """
        Load and process documents.

        Returns:
            List of processed documents or None if failed
        """
        try:
            raw_docs = self.document_loader.load_all_documents()

            if not raw_docs:
                logger.warning("No documents found to process")
                return None

            split_docs = self.document_processor.chunk_documents(raw_docs)
            keywords = self.keyword_extractor.extract_keywords(split_docs)
            self.relevance_checker = SmartRelevanceChecker(keywords)

            logger.info(f"Processed {len(split_docs)} document chunks")
            return split_docs
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return None

    def setup_vectorstore(self, connection_string: str, documents: List[Any], force_rebuild: bool = False) -> bool:
        """
        Setup vector store.

        Args:
            connection_string: Database connection string
            documents: Documents to ingest
            force_rebuild: Whether to force rebuild the collection

        Returns:
            True if setup successful, False otherwise
        """
        try:
            self.vectorstore_manager = VectorStoreManager(connection_string, COLLECTION_NAME)

            vs = self.vectorstore_manager.get_or_create_vectorstore(documents, force_rebuild=force_rebuild)

            # Store vectorstore for later use
            self._vectorstore = vs
            logger.info("Vector store setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Vector store setup failed: {e}")
            return False

    def setup_qa_chain(self) -> bool:
        """
        Setup QA chain.

        Returns:
            True if setup successful, False otherwise
        """
        try:
            if not hasattr(self, "_vectorstore"):
                logger.error("Vector store not initialized")
                return False

            retriever = self.vectorstore_manager.build_retriever(self._vectorstore, PROBLEM_ID)

            from src.core.config import GEMINI_API_KEY

            if GEMINI_API_KEY:
                self.qa_chain = self.llm_builder.build_qa_chain(retriever)
                logger.info("QA chain setup completed successfully with real LLM")
            else:
                raise Exception("No API key provided")

            return True
        except Exception as e:
            logger.error(f"QA chain setup failed: {e}")
            return False

    def process_question(self, question: str) -> Tuple[str, List[Any], bool]:
        """
        Process a user question.

        Args:
            question: User question

        Returns:
            Tuple of (answer, sources, is_relevant)
        """
        if not self.qa_chain:
            return "QA chain not initialized", [], False

        # Relevance checking temporarily disabled
        # if not self.relevance_checker:
        #     return "System not properly initialized", [], False
        # if not self.relevance_checker.is_relevant(question):
        #     return REFUSAL_MSG, [], False

        try:
            # Process with QA chain
            result = self.qa_chain.invoke({"query": question})
            answer = result.get("result", "")
            sources = result.get("source_documents", [])

            # Handle empty answer
            if not answer.strip():
                answer = REFUSAL_MSG

            return answer, sources, True
        except Exception as e:
            error_msg = f"Error processing question: {e}"
            logger.error(error_msg)
            return error_msg, [], False

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status information.

        Returns:
            Dictionary with system status
        """
        status = {
            "database_initialized": self.database_manager is not None,
            "vectorstore_initialized": self.vectorstore_manager is not None,
            "qa_chain_initialized": self.qa_chain is not None,
            "relevance_checker_initialized": self.relevance_checker is not None,
            "relevance_checking_disabled": True,  # Indicate that relevance checking is disabled
        }

        if self.database_manager:
            status["database_connection"] = self.database_manager.test_connection()

        return status

    def initialize_system(self, connection_string: str = None, **db_params) -> bool:
        """
        Initialize the complete system.

        Args:
            connection_string: Database connection string
            **db_params: Database parameters

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Setup database
            if not self.setup_database(connection_string, **db_params):
                return False

            # Load and process documents
            documents = self.load_and_process_documents()
            if documents is None:
                return False

            # Setup vector store
            conn_str = connection_string
            if not conn_str and db_params:
                conn_str = (
                    f"postgresql+psycopg://{db_params['user']}:{db_params['password']}"
                    f"@{db_params['host']}:{db_params['port']}/{db_params['database']}"
                )

            if not self.setup_vectorstore(conn_str, documents):
                return False

            # Setup QA chain
            if not self.setup_qa_chain():
                return False

            logger.info("System initialization completed successfully")
            return True
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            return False


# Convenience functions for testing
def create_chatbot() -> ChatbotLogic:
    """Create a new chatbot instance."""
    return ChatbotLogic()


def test_chatbot_initialization(connection_string: str = None, **db_params) -> bool:
    """
    Test chatbot initialization.

    Args:
        connection_string: Database connection string
        **db_params: Database parameters

    Returns:
        True if initialization successful, False otherwise
    """
    chatbot = create_chatbot()
    return chatbot.initialize_system(connection_string, **db_params)


def test_question_processing(question: str, connection_string: str = None, **db_params) -> Tuple[str, List[Any], bool]:
    """
    Test question processing.

    Args:
        question: Question to test
        connection_string: Database connection string
        **db_params: Database parameters

    Returns:
        Tuple of (answer, sources, is_relevant)
    """
    chatbot = create_chatbot()

    if not chatbot.initialize_system(connection_string, **db_params):
        return "System initialization failed", [], False

    return chatbot.process_question(question)
