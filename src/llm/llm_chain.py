"""
LLM chain and QA operations.
"""

import os

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import GEMINI_API_KEY, GEMINI_MODEL


class LLMChainBuilder:
    """Builds and manages LLM chains for QA operations."""

    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
        self.api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)

    def build_qa_chain(self, retriever) -> RetrievalQA:
        """
        Build a RetrievalQA chain with Gemini LLM.

        Args:
            retriever: Retriever instance

        Returns:
            RetrievalQA chain instance
        """
        llm = ChatGoogleGenerativeAI(model=self.model_name, convert_system_message_to_human=True, api_key=self.api_key)

        prompt = self._create_qa_prompt()

        chain = RetrievalQA.from_chain_type(
            llm=llm,
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
