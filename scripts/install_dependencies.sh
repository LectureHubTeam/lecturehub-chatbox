#!/bin/bash

echo "Installing LectureHub Chatbot Dependencies..."
echo "=============================================="

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install core dependencies
echo "Installing core dependencies..."
pip install -r requirements.txt

# Install additional dependencies that might be needed
echo "Installing additional dependencies..."
pip install pgvector psycopg

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest black flake8

echo "=============================================="
echo "Dependencies installation completed!"
echo ""
echo "To test the installation, run:"
echo "  python test_logic.py"
echo ""
echo "To start the application, run:"
echo "  streamlit run main.py"
