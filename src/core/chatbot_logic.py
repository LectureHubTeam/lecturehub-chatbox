"""
Core chatbot logic separated from Streamlit UI.

This module contains all the business logic that can be tested independently
without requiring Streamlit context.
"""

from typing import Any, Dict, List, Optional, Tuple

from src.core.config import REFUSAL_MSG
from src.database import DatabaseManager, VectorStoreManager
from src.llm import KeywordExtractor, LLMChainBuilder
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
        self.memory_manager = None
        self.vectorstore_manager = None
        self.relevance_checker = None
        self.qa_chain = None
        self.database_manager = None
        self.current_problem = None

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

    def load_and_process_documents(self, problem_name: str) -> Optional[List[Any]]:
        """
        Load and process documents for a specific problem.

        Args:
            problem_name: Name of the problem

        Returns:
            List of processed documents or None if failed
        """
        try:
            raw_docs = self.document_loader.load_problem_documents(problem_name)

            if not raw_docs:
                logger.warning(f"No documents found for problem: {problem_name}")
                return None

            split_docs = self.document_processor.chunk_documents(raw_docs, problem_name)

            logger.info(f"Processed {len(split_docs)} document chunks for problem: {problem_name}")
            return split_docs
        except Exception as e:
            logger.error(f"Document processing failed for problem {problem_name}: {e}")
            return None

    def setup_vectorstore(
        self, connection_string: str, problem_name: str, documents: List[Any], force_rebuild: bool = False
    ) -> bool:
        """
        Setup vector store for a specific problem.

        Args:
            connection_string: Database connection string
            problem_name: Name of the problem
            documents: Documents to ingest
            force_rebuild: Whether to force rebuild the collection

        Returns:
            True if setup successful, False otherwise
        """
        try:
            self.vectorstore_manager = VectorStoreManager(connection_string, problem_name)
            self.current_problem = problem_name

            vs = self.vectorstore_manager.get_or_create_vectorstore(documents, force_rebuild=force_rebuild)

            # Store vectorstore for later use
            self._vectorstore = vs
            logger.info(f"Vector store setup completed successfully for problem: {problem_name}")
            return True
        except Exception as e:
            logger.error(f"Vector store setup failed for problem {problem_name}: {e}")
            return False

    def setup_vectorstore_from_existing(self, connection_string: str, problem_name: str) -> bool:
        """
        Setup vector store from existing data without re-processing documents.

        Args:
            connection_string: Database connection string
            problem_name: Name of the problem

        Returns:
            True if setup successful, False otherwise
        """
        try:
            self.vectorstore_manager = VectorStoreManager(connection_string, problem_name)
            self.current_problem = problem_name

            # Try to connect to existing collection
            vs = self.vectorstore_manager.get_or_create_vectorstore([], force_rebuild=False)

            # Test if collection has data
            try:
                test_result = vs.similarity_search("test", k=1)
                if test_result:
                    self._vectorstore = vs
                    logger.info(f"Loaded existing vector store for problem: {problem_name}")
                    return True
                else:
                    logger.info(f"No existing data found for problem: {problem_name}")
                    return False
            except Exception:
                logger.info(f"Collection not found or empty for problem: {problem_name}")
                return False

        except Exception as e:
            logger.error(f"Error loading existing vector store for problem {problem_name}: {e}")
            return False

    def setup_memory(self, memory_type: str = "buffer_window", k: int = 5) -> bool:
        """
        Setup memory manager.

        Args:
            memory_type: Type of memory ("buffer_window", "summary", "hybrid")
            k: Number of messages to keep in buffer

        Returns:
            True if setup successful, False otherwise
        """
        try:
            from src.memory import ChatMemoryManager

            self.memory_manager = ChatMemoryManager(memory_type=memory_type, k=k)
            logger.info(f"Memory manager setup completed successfully with type: {memory_type}")
            return True
        except Exception as e:
            logger.error(f"Memory setup failed: {e}")
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

            retriever = self.vectorstore_manager.build_retriever(self._vectorstore)

            from src.core.config import GEMINI_API_KEY

            if not GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY is required but not provided")
                return False

            # Setup memory if not already done
            if not self.memory_manager:
                self.setup_memory()

            # Build QA chain with memory
            self.qa_chain = self.llm_builder.build_qa_chain(retriever, self.memory_manager)
            logger.info("QA chain setup completed successfully")

            return True
        except Exception as e:
            logger.error(f"QA chain setup failed: {e}")
            return False

    def _handle_specific_question(self, question: str) -> str:
        """
        Handle specific question.
        """
        greeting_questions = ["hello", "hi", "hey", "xin chào", "chào bạn", "chào"]
        goodbye_questions = ["cảm ơn", "cảm ơn bạn", "thanks", "thank you"]
        insult_questions = ["ngu", "dốt", "tệ", "đần độn", "đéo", "chó", "bò", "lợn", "heo"]
        sensitive_questions = ["lồn", "cặc", "địt", "xàm", "mất dạy"]

        response = None

        if question.lower() in greeting_questions:
            response = "Xin chào, tôi là trợ lý AI giúp bạn hỏi sâu về bài giảng này."

        if question.lower() in goodbye_questions:
            response = "Không có gì, tôi chỉ là một trợ lý AI giúp bạn hỏi sâu về bài giảng này."

        if question.lower() in insult_questions:
            response = "Ngưng phán xét. OK?"

        if question.lower() in sensitive_questions:
            response = "Ngưng văng tục. OK?"

        return response

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

        response = self._handle_specific_question(question)
        if response:
            return response, [], True

        try:
            # Add question to memory
            if self.memory_manager:
                self.memory_manager.add_user_message(question)
            # Process with QA chain
            # ConversationalRetrievalChain uses "question" as input key
            if hasattr(self.qa_chain, "memory") and self.qa_chain.memory:
                # This is a ConversationalRetrievalChain with memory
                result = self.qa_chain.invoke({"question": question})
            else:
                # This is a regular RetrievalQA chain
                result = self.qa_chain.invoke({"query": question})
            # Get answer from different possible keys
            answer = result.get("result", result.get("answer", ""))
            sources = result.get("source_documents", [])

            # Add answer to memory
            if self.memory_manager:
                self.memory_manager.add_ai_message(answer)

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
            "memory_initialized": self.memory_manager is not None,
        }

        if self.database_manager:
            status["database_connection"] = self.database_manager.test_connection()

        return status

    def initialize_system(self, problem_name: str, connection_string: str = None, **db_params) -> bool:
        """
        Initialize the complete system for a specific problem.

        Args:
            problem_name: Name of the problem
            connection_string: Database connection string
            **db_params: Database parameters

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.current_problem = problem_name

            # Setup database
            if not self.setup_database(connection_string, **db_params):
                return False

            # Load and process documents
            documents = self.load_and_process_documents(problem_name)
            if documents is None:
                return False

            # Setup vector store
            conn_str = connection_string
            if not conn_str and db_params:
                conn_str = (
                    f"postgresql+psycopg://{db_params['user']}:{db_params['password']}"
                    f"@{db_params['host']}:{db_params['port']}/{db_params['database']}"
                )

            if not self.setup_vectorstore(conn_str, problem_name, documents):
                return False

            # Setup QA chain
            if not self.setup_qa_chain():
                return False

            logger.info(f"System initialization completed successfully for problem: {problem_name}")
            return True
        except Exception as e:
            logger.error(f"System initialization failed for problem {problem_name}: {e}")
            return False


# Convenience functions for testing
def create_chatbot() -> ChatbotLogic:
    """Create a new chatbot instance."""
    return ChatbotLogic()


def test_chatbot_initialization(problem_name: str, connection_string: str = None, **db_params) -> bool:
    """
    Test chatbot initialization.

    Args:
        problem_name: Name of the problem
        connection_string: Database connection string
        **db_params: Database parameters

    Returns:
        True if initialization successful, False otherwise
    """
    chatbot = create_chatbot()
    return chatbot.initialize_system(problem_name, connection_string, **db_params)


def test_question_processing(
    question: str, problem_name: str, connection_string: str = None, **db_params
) -> Tuple[str, List[Any], bool]:
    """
    Test question processing.

    Args:
        question: Question to test
        problem_name: Name of the problem
        connection_string: Database connection string
        **db_params: Database parameters

    Returns:
        Tuple of (answer, sources, is_relevant)
    """
    chatbot = create_chatbot()

    if not chatbot.initialize_system(problem_name, connection_string, **db_params):
        return "System initialization failed", [], False

    return chatbot.process_question(question)
