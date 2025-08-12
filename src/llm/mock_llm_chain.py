"""
Mock LLM chain for testing without API key.
"""

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel


class MockLLM(BaseLanguageModel):
    """Mock LLM that returns predefined responses for testing."""

    def __init__(self):
        self.responses = {
            "sample input": "Sample input của đề bao gồm:\n1. Một số nguyên k (khóa dịch chuyển)\n2. Một chuỗi ký tự (văn bản đã mã hóa)",
            "tên đề": "Tên đề là: Giải mã Caesar Cipher",
            "input output": "Input mà đề yêu cầu bao gồm:\n1. Một số nguyên biểu thị số lượng dịch chuyển (khóa dịch chuyển).\n2. Một chuỗi ký tự là văn bản đã mã hóa.\n\nOutput mà đề yêu cầu là văn bản gốc đã được giải mã, được tạo thành bằng cách nối các ký tự đã giải mã lại với nhau.",
            "default": "Dựa trên context được cung cấp, đây là câu trả lời cho câu hỏi của bạn.",
        }

    def invoke(self, input_text: str, **kwargs):
        """Return a mock response based on input."""
        input_lower = input_text.lower()

        if "sample input" in input_lower or "input" in input_lower:
            return self.responses["sample input"]
        elif "tên đề" in input_lower or "tên" in input_lower:
            return self.responses["tên đề"]
        elif "input output" in input_lower or "output" in input_lower:
            return self.responses["input output"]
        else:
            return self.responses["default"]

    @property
    def _llm_type(self) -> str:
        return "mock"


class MockLLMChainBuilder:
    """Builds mock LLM chains for testing."""

    def __init__(self):
        self.llm = MockLLM()

    def build_qa_chain(self, retriever) -> RetrievalQA:
        """
        Build a mock RetrievalQA chain.

        Args:
            retriever: Retriever instance

        Returns:
            RetrievalQA chain instance
        """
        prompt = self._create_qa_prompt()

        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )
        return chain

    def _create_qa_prompt(self) -> PromptTemplate:
        """Create the QA prompt template."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Bạn là chatbot hỗ trợ học bài giảng. "
                "Chỉ trả lời dựa trên context sau về bài toán này. "
                "Nếu câu hỏi không liên quan đến đề bài, bài giảng hoặc code, "
                "hãy trả lời: 'Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi.'\n\n"
                "Context:\n{context}\n\nCâu hỏi: {question}"
            ),
        )
