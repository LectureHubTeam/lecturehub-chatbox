"""
Vector store operations and embeddings management.
"""

from typing import Any, List

from langchain_community.vectorstores.pgvector import PGVector
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.config import DEFAULT_K_RETRIEVAL, DEVICE, EMBEDDING_MODEL_NAME, get_collection_name


class EmbeddingManager:
    """Manages embedding operations."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of EmbeddingManager exists."""
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize embedding manager. Only initializes once."""
        # Only initialize once
        if self._initialized:
            return

        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": DEVICE}, encode_kwargs={"device": DEVICE}
        )

        self._initialized = True

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get the embedding model instance."""
        return self.embeddings


class VectorStoreManager:
    """Manages vector store operations."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of VectorStoreManager exists."""
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, connection_string: str, problem_name: str):
        """
        Initialize vector store manager. Only initializes once.

        Args:
            connection_string: Database connection string
            problem_name: Name of the problem
        """
        # Reset if problem_name changes
        if hasattr(self, "problem_name") and self.problem_name != problem_name:
            self._reset_instance()

        # Only initialize once
        if self._initialized:
            return

        self.connection_string = connection_string
        self.problem_name = problem_name
        self.collection_name = get_collection_name(problem_name)
        self.embedding_manager = EmbeddingManager()

        self._initialized = True

    def _reset_instance(self):
        """Reset the singleton instance for new problem."""
        VectorStoreManager._instance = None
        VectorStoreManager._initialized = False
        self._initialized = False

    def rebuild_collection(self, documents: List[Any]) -> PGVector:
        """
        Create/recreate a PGVector collection and ingest documents.

        Args:
            documents: List of documents to ingest

        Returns:
            PGVector instance
        """
        embeddings = self.embedding_manager.get_embeddings()
        vs = PGVector.from_documents(
            documents=documents,
            embedding=embeddings,
            connection_string=self.connection_string,
            collection_name=self.collection_name,
            pre_delete_collection=True,
            use_jsonb=True,
        )
        return vs

    def get_or_create_vectorstore(self, docs: List[Any], force_rebuild: bool = False) -> PGVector:
        """
        Get existing vector store or create new one.

        Args:
            docs: Documents to ingest if creating new store
            force_rebuild: Whether to force rebuild the collection

        Returns:
            PGVector instance
        """
        embeddings = self.embedding_manager.get_embeddings()

        if force_rebuild:
            return self.rebuild_collection(docs)

        # Try to connect to existing collection
        try:
            vs = PGVector(
                connection_string=self.connection_string,
                collection_name=self.collection_name,
                embedding_function=embeddings,
                use_jsonb=True,
            )

            # Test if collection exists and has data
            try:
                _ = vs.similarity_search("test", k=1)
            except Exception:
                # Collection likely missing or empty; rebuild
                vs = self.rebuild_collection(docs)
        except Exception:
            # Could not initialize; attempt rebuild
            vs = self.rebuild_collection(docs)

        return vs

    def build_retriever(self, vs: PGVector, k: int = DEFAULT_K_RETRIEVAL):
        """
        Build a retriever with problem_name filtering.

        Args:
            vs: PGVector instance
            k: Number of documents to retrieve

        Returns:
            Retriever instance
        """
        # Create a retriever with problem_name filtering
        retriever = vs.as_retriever(search_kwargs={"k": k})

        # Since we're using separate collections per problem,
        # the filtering is already handled by the collection itself
        # No need for additional filtering
        return retriever
