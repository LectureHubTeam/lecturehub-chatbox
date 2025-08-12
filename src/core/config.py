"""
Configuration settings for the RAG Chatbot application.
"""

import os
from typing import Final

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
PROBLEM_ID: Final[str] = "ma_de_001"
COLLECTION_NAME: Final[str] = f"rag_{PROBLEM_ID}"
EMBEDDING_MODEL_NAME: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM: Final[int] = 384
REFUSAL_MSG: Final[str] = "Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi."

# File Configuration
REQUIRED_FILES: Final[dict] = {
    "pdf": "data/lectures/mmceasar2/mmceasar2.pdf",
    "markdown": "data/lectures/mmceasar2/mmceasar2.md",
    "python": "data/lectures/mmceasar2/mmceasar2.py",
}

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
