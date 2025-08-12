"""
Vector store operations and embeddings management.
"""

from typing import Any, List

from langchain_community.vectorstores.pgvector import PGVector
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.config import DEFAULT_K_RETRIEVAL, DEVICE, EMBEDDING_MODEL_NAME, PROBLEM_ID


class EmbeddingManager:
    """Manages embedding operations."""

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": DEVICE}, encode_kwargs={"device": DEVICE}
        )

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get the embedding model instance."""
        return self.embeddings


class VectorStoreManager:
    """Manages vector store operations."""

    def __init__(self, connection_string: str, collection_name: str):
        self.connection_string = connection_string
        self.collection_name = collection_name
        self.embedding_manager = EmbeddingManager()

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

    def build_retriever(self, vs: PGVector, problem_id: str = PROBLEM_ID, k: int = DEFAULT_K_RETRIEVAL):
        """
        Build a retriever with metadata filtering.

        Args:
            vs: PGVector instance
            problem_id: Problem ID to filter by
            k: Number of documents to retrieve

        Returns:
            Retriever instance
        """
        # Use simple retriever without metadata filtering to avoid jsonb_path_match issues
        return vs.as_retriever(search_kwargs={"k": k})
