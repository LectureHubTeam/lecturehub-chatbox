"""
Document loading and processing functionality.
"""

import os
from typing import Any, List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from src.utils.logger import logger

try:
    from langchain_community.document_loaders import UnstructuredMarkdownLoader

    HAS_UNSTRUCTURED = True
except Exception:
    UnstructuredMarkdownLoader = None
    HAS_UNSTRUCTURED = False

from src.core.config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, PROBLEM_ID, REQUIRED_FILES


class DocumentLoader:
    """Handles loading and processing of documents."""

    def __init__(self):
        self.supported_file_types = {
            "pdf": self._load_pdf,
            "markdown": self._load_markdown,
            "python": self._load_python,
        }

    def load_all_documents(self) -> List[Any]:
        """
        Load all required documents and return a list of LangChain Documents.

        Returns:
            List of LangChain Document objects with metadata
        """
        docs = []

        for file_type, file_path in REQUIRED_FILES.items():
            if file_type in self.supported_file_types:
                file_docs = self.supported_file_types[file_type](file_path)
                docs.extend(file_docs)

        return docs

    def _load_pdf(self, file_path: str) -> List[Any]:
        """Load PDF document."""
        if not os.path.exists(file_path):
            logger.warning(f"Thiếu file '{file_path}'.")
            return []

        try:
            loader = PyPDFLoader(file_path)
            pdf_docs = loader.load()
            for doc in pdf_docs:
                doc.metadata = {**doc.metadata, "file_type": "pdf", "problem_id": PROBLEM_ID}
            return pdf_docs
        except Exception:
            return []

    def _load_markdown(self, file_path: str) -> List[Any]:
        """Load Markdown document."""
        if not os.path.exists(file_path):
            logger.warning(f"Thiếu file '{file_path}'.")
            return []

        try:
            if HAS_UNSTRUCTURED:
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding="utf-8")

            md_docs = loader.load()
            for doc in md_docs:
                doc.metadata = {**doc.metadata, "file_type": "md", "problem_id": PROBLEM_ID}
            return md_docs
        except Exception:
            logger.warning(f"Không thể load Markdown '{file_path}'.")
            return []

    def _load_python(self, file_path: str) -> List[Any]:
        """Load Python code document."""
        if not os.path.exists(file_path):
            logger.warning(f"Thiếu file '{file_path}'.")
            return []

        try:
            loader = TextLoader(file_path, encoding="utf-8")
            py_docs = loader.load()
            for doc in py_docs:
                doc.metadata = {**doc.metadata, "file_type": "py", "problem_id": PROBLEM_ID}
            return py_docs
        except Exception:
            logger.warning(f"Không thể load Python '{file_path}'.")
            return []


class DocumentProcessor:
    """Handles document chunking and processing."""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def chunk_documents(self, docs: List[Any]) -> List[Any]:
        """
        Split documents into chunks while preserving metadata.

        Args:
            docs: List of LangChain Document objects

        Returns:
            List of chunked Document objects
        """
        split_docs = self.splitter.split_documents(docs)

        # Ensure metadata carries over problem_id and file_type
        for doc in split_docs:
            doc.metadata = {
                **doc.metadata,
                "problem_id": doc.metadata.get("problem_id", PROBLEM_ID),
                "file_type": doc.metadata.get("file_type", "unknown"),
            }

        return split_docs
