#!/usr/bin/env python3
"""
Test script to check mock LLM functionality.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_mock_llm():
    """Test mock LLM functionality."""
    print("Testing Mock LLM")
    print("=" * 30)

    try:
        from src.llm.mock_llm_chain import MockLLM, MockLLMChainBuilder

        # Test MockLLM directly
        print("1. Testing MockLLM directly...")
        mock_llm = MockLLM()

        test_inputs = [
            "sample input của đề là gì",
            "Tên đề à gì",
            "Giải thích input, output mà đề yêu cầu",
            "Cách giải mã Caesar?",
        ]

        for i, test_input in enumerate(test_inputs, 1):
            response = mock_llm.invoke(test_input)
            print(f"   {i}. Input: {test_input}")
            print(f"      Response: {response[:100]}...")

        # Test MockLLMChainBuilder
        print("\n2. Testing MockLLMChainBuilder...")
        mock_builder = MockLLMChainBuilder()
        print("   ✅ MockLLMChainBuilder created successfully")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_mock_llm()
