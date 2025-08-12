#!/usr/bin/env python3
"""
Script to fix all dependency issues for LectureHub Chatbot.
"""

import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main function to fix dependencies."""
    print("🔧 LectureHub Chatbot - Dependency Fix Script")
    print("=" * 60)

    # Check if we're in a virtual environment
    if not hasattr(sys, "real_prefix") and not (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: You might not be in a virtual environment.")
        print("   Consider creating one: python -m venv venv && source venv/bin/activate")

    # Step 1: Upgrade pip
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return 1

    # Step 2: Uninstall conflicting packages
    print("\n🧹 Cleaning up conflicting packages...")
    packages_to_remove = ["psycopg2-binary", "psycopg2", "langchain-community"]

    for package in packages_to_remove:
        run_command(f"pip uninstall -y {package}", f"Removing {package}")

    # Step 3: Install core dependencies
    if not run_command("pip install psycopg pgvector", "Installing PostgreSQL dependencies"):
        return 1

    # Step 4: Install LangChain packages
    langchain_packages = ["langchain", "langchain-community", "langchain-google-genai"]

    for package in langchain_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return 1

    # Step 5: Install other dependencies
    other_packages = ["streamlit", "python-dotenv", "sentence-transformers", "pypdf", "unstructured", "markdown"]

    for package in other_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return 1

    # Step 6: Test imports
    print("\n🧪 Testing imports...")
    test_imports = [
        "import psycopg",
        "import pgvector",
        "from langchain_community.vectorstores.pgvector import PGVector",
        "from langchain_community.embeddings import HuggingFaceEmbeddings",
        "import streamlit",
    ]

    for import_stmt in test_imports:
        try:
            exec(import_stmt)
            print(f"✅ {import_stmt}")
        except ImportError as e:
            print(f"❌ {import_stmt} - {e}")
            return 1

    print("\n🎉 All dependencies fixed successfully!")
    print("\nYou can now run:")
    print("  python test_logic.py")
    print("  streamlit run main.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
