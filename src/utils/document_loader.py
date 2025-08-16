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

# Import config values directly to avoid circular imports
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

# Import get_problem_files function directly
LECTURES_DIR = "data/lectures"


def get_problem_files(problem_name: str) -> dict:
    """Get file paths for a specific problem."""
    problem_dir = os.path.join(LECTURES_DIR, problem_name)
    if not os.path.exists(problem_dir):
        return {}

    files = {}
    for file in os.listdir(problem_dir):
        file_path = os.path.join(problem_dir, file)
        if file.endswith(".pdf"):
            files["pdf"] = file_path
        elif file.endswith(".md"):
            files["markdown"] = file_path
        elif file.endswith(".py"):
            files["python"] = file_path

    return files


class DocumentLoader:
    """Handles loading and processing of documents."""

    def __init__(self):
        self.supported_file_types = {
            "pdf": self._load_pdf,
            "markdown": self._load_markdown,
            "python": self._load_python,
        }

    def load_problem_documents(self, problem_name: str) -> List[Any]:
        """
        Load all documents for a specific problem.

        Args:
            problem_name: Name of the problem folder

        Returns:
            List of LangChain Document objects with metadata
        """
        docs = []
        problem_files = get_problem_files(problem_name)

        for file_type, file_path in problem_files.items():
            if file_type in self.supported_file_types:
                file_docs = self.supported_file_types[file_type](file_path, problem_name)
                docs.extend(file_docs)

        return docs

    def _load_pdf(self, file_path: str, problem_name: str) -> List[Any]:
        """Load PDF document."""
        if not os.path.exists(file_path):
            logger.warning(f"Thiếu file '{file_path}'.")
            return []

        try:
            loader = PyPDFLoader(file_path)
            pdf_docs = loader.load()
            for doc in pdf_docs:
                doc.metadata = {**doc.metadata, "file_type": "pdf", "problem_name": problem_name}
            return pdf_docs
        except Exception:
            return []

    def _load_markdown(self, file_path: str, problem_name: str) -> List[Any]:
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
                doc.metadata = {**doc.metadata, "file_type": "md", "problem_name": problem_name}
            return md_docs
        except Exception:
            logger.warning(f"Không thể load Markdown '{file_path}'.")
            return []

    def _load_python(self, file_path: str, problem_name: str) -> List[Any]:
        """Load Python code document."""
        if not os.path.exists(file_path):
            logger.warning(f"Thiếu file '{file_path}'.")
            return []

        try:
            loader = TextLoader(file_path, encoding="utf-8")
            py_docs = loader.load()
            for doc in py_docs:
                doc.metadata = {**doc.metadata, "file_type": "py", "problem_name": problem_name}
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

    def chunk_documents(self, docs: List[Any], problem_name: str) -> List[Any]:
        """
        Split documents into chunks while preserving metadata.

        Args:
            docs: List of LangChain Document objects
            problem_name: Name of the problem

        Returns:
            List of chunked Document objects
        """
        split_docs = self.splitter.split_documents(docs)

        # Ensure metadata carries over problem_name and file_type
        for doc in split_docs:
            doc.metadata = {
                **doc.metadata,
                "problem_name": doc.metadata.get("problem_name", problem_name),
                "file_type": doc.metadata.get("file_type", "unknown"),
            }

        return split_docs
