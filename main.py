"""
Main entry point for the LectureHub Chatbot application.

This is the entry point for the refactored application with modular structure.
"""

import os
import sys

from src.core.main import main

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


if __name__ == "__main__":
    main()
