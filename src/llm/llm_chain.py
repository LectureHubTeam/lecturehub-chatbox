"""
LLM chain and QA operations with memory support.
"""

import os

from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import GEMINI_API_KEY, GEMINI_MODEL

# from src.memory import ChatMemoryManager


class LLMChainBuilder:
    """Builds and manages LLM chains for QA operations with memory."""

    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
        self.api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)

    def build_qa_chain(self, retriever, memory_manager=None):
        """
        Build a ConversationalRetrievalChain with Gemini LLM and memory.

        Args:
            retriever: Retriever instance
            memory_manager: Memory manager instance

        Returns:
            ConversationalRetrievalChain instance
        """
        llm = ChatGoogleGenerativeAI(model=self.model_name, convert_system_message_to_human=True, api_key=self.api_key)

        # Create prompt template with memory support
        prompt = self._create_qa_prompt()

        # Build chain with memory
        if memory_manager and memory_manager.memory:
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                memory=memory_manager.memory,
                combine_docs_chain_kwargs={"prompt": prompt},
                return_source_documents=True,
                output_key="answer",
                verbose=False,
            )
        else:
            # Fallback to simple RetrievalQA if no memory
            from langchain.chains import RetrievalQA

            chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True,
            )

        return chain

    def _create_qa_prompt(self) -> PromptTemplate:
        """Create the QA prompt template with memory support."""
        return PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template=(
                "Bạn là một trợ lý AI thân thiện và hữu ích, chuyên hỗ trợ học sinh học tập về bài toán Caesar Cipher. "
                "Hãy trả lời câu hỏi dựa trên thông tin trong context được cung cấp và lịch sử hội thoại trước đó.\n\n"
                "Hướng dẫn trả lời:\n"
                "1. Trả lời ngắn gọn và trực tiếp cho câu hỏi đơn giản\n"
                "2. Trả lời chi tiết và rõ ràng cho câu hỏi phức tạp\n"
                "3. Sử dụng giọng điệu thân thiện, khuyến khích học tập\n"
                "4. Cung cấp giải thích và ví dụ khi cần thiết\n"
                "5. Luôn trả lời bằng tiếng Việt\n"
                "6. Tham khảo lịch sử hội thoại để hiểu context của câu hỏi\n"
                "7. Nếu câu hỏi không liên quan đến bài toán này, hãy trả lời: 'Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi.'\n\n"
                "Lịch sử hội thoại:\n{chat_history}\n\n"
                "Context (tài liệu tham khảo):\n{context}\n\n"
                "Câu hỏi hiện tại: {question}\n\n"
                "Trả lời:"
            ),
        )

    def build_simple_qa_chain(self, retriever):
        """
        Build a simple RetrievalQA chain without memory (for backward compatibility).

        Args:
            retriever: Retriever instance

        Returns:
            RetrievalQA chain instance
        """
        from langchain.chains import RetrievalQA

        llm = ChatGoogleGenerativeAI(model=self.model_name, convert_system_message_to_human=True, api_key=self.api_key)

        prompt = self._create_simple_prompt()

        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )
        return chain

    def _create_simple_prompt(self) -> PromptTemplate:
        """Create a simple QA prompt template without memory."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Bạn là một trợ lý AI thân thiện và hữu ích, chuyên hỗ trợ học sinh học tập về bài toán Caesar Cipher. "
                "Hãy trả lời câu hỏi dựa trên thông tin trong context được cung cấp.\n\n"
                "Hướng dẫn trả lời:\n"
                "1. Trả lời ngắn gọn và trực tiếp cho câu hỏi đơn giản\n"
                "2. Trả lời chi tiết và rõ ràng cho câu hỏi phức tạp\n"
                "3. Sử dụng giọng điệu thân thiện, khuyến khích học tập\n"
                "4. Cung cấp giải thích và ví dụ khi cần thiết\n"
                "5. Luôn trả lời bằng tiếng Việt\n"
                "6. Nếu câu hỏi không liên quan đến bài toán này, hãy trả lời: 'Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi.'\n\n"
                "Context:\n{context}\n\nCâu hỏi: {question}\n\nTrả lời:"
            ),
        )
