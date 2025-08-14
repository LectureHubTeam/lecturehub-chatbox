"""
Configuration settings for the RAG Chatbot application.
"""

import os
from typing import Final, List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_HOST: Final[str] = os.getenv("DB_HOST", "localhost")
DB_PORT: Final[str] = os.getenv("DB_PORT", "5432")
DB_NAME: Final[str] = os.getenv("DB_NAME", "embedding")
DB_USER: Final[str] = os.getenv("DB_USER", "root")
DB_PASSWORD: Final[str] = os.getenv("DB_PASSWORD", "root_password")

# Construct connection string from components
DEFAULT_CONN_STR: Final[str] = os.getenv(
    "PG_CONN", f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Application Configuration
LECTURES_DIR: Final[str] = "data/lectures"
EMBEDDING_MODEL_NAME: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM: Final[int] = 384
REFUSAL_MSG: Final[str] = "Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi."

# Chunking Configuration
DEFAULT_CHUNK_SIZE: Final[int] = 500
DEFAULT_CHUNK_OVERLAP: Final[int] = 50

# Retrieval Configuration
DEFAULT_K_RETRIEVAL: Final[int] = 5
DEFAULT_MAX_KEYWORDS: Final[int] = 40

# LLM Configuration
GEMINI_MODEL: Final[str] = "gemini-2.5-flash-lite"
GEMINI_API_KEY: Final[str] = os.getenv("GEMINI_API_KEY")

# Relevance Checker Configuration
RELEVANCE_THRESHOLD: Final[float] = 0.5

DEVICE: Final[str] = os.getenv("DEVICE", "cpu")


def get_available_problems() -> List[str]:
    """
    Get list of available problems from data/lectures directory.

    Returns:
        List of problem names (folder names)
    """
    if not os.path.exists(LECTURES_DIR):
        return []

    problems = []
    for item in os.listdir(LECTURES_DIR):
        item_path = os.path.join(LECTURES_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            # Check if folder contains at least one supported file
            supported_files = [f for f in os.listdir(item_path) if f.endswith((".pdf", ".md", ".py"))]
            if supported_files:
                problems.append(item)

    return sorted(problems)


def get_problem_files(problem_name: str) -> dict:
    """
    Get file paths for a specific problem.

    Args:
        problem_name: Name of the problem folder

    Returns:
        Dictionary with file paths for the problem
    """
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


def get_collection_name(problem_name: str) -> str:
    """
    Get collection name for a problem.

    Args:
        problem_name: Name of the problem

    Returns:
        Collection name for the problem
    """
    return f"rag_{problem_name}"
