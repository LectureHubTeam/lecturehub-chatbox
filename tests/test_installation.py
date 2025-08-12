#!/usr/bin/env python3
"""
Test script to verify all dependencies are properly installed.
"""

import importlib
import sys


def test_import(module_name: str, package_name: str = None) -> bool:
    """Test if a module can be imported."""
    try:
        if package_name:
            importlib.import_module(package_name)
        else:
            importlib.import_module(module_name)
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False


def main():
    """Test all required dependencies."""
    print("Testing LectureHub Chatbot Dependencies")
    print("=" * 50)

    # Core dependencies
    dependencies = [
        ("streamlit", "streamlit"),
        ("langchain", "langchain"),
        ("langchain_community", "langchain_community"),
        ("langchain_google_genai", "langchain_google_genai"),
        ("langchain_postgres", "langchain_postgres"),
        ("langchain_huggingface", "langchain_huggingface"),
        ("psycopg", "psycopg"),
        ("pgvector", "pgvector"),
        ("python_dotenv", "dotenv"),
        ("sentence_transformers", "sentence_transformers"),
        ("pypdf", "pypdf"),
        ("unstructured", "unstructured"),
        ("markdown", "markdown"),
    ]

    all_passed = True

    for module_name, package_name in dependencies:
        print(f"Testing {module_name}...", end=" ")
        if test_import(module_name, package_name):
            print("✅")
        else:
            print("❌")
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 All dependencies are properly installed!")
        print("\nYou can now run:")
        print("  python test_logic.py")
        print("  streamlit run main.py")
    else:
        print("❌ Some dependencies are missing!")
        print("\nPlease run:")
        print("  ./install_dependencies.sh")
        print("  or")
        print("  pip install -r requirements.txt")
        print("  pip install pgvector psycopg")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
