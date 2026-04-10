from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
    1. Retrieve top-k relevant chunks from the store.
    2. Build a prompt with the chunks as context.
    3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        chunks = self.store.search(question, top_k=top_k)
        if not chunks:
            return "Tôi không có đủ thông tin trong ngữ cảnh đã truy xuất để trả lời câu hỏi này."

        context = "\n\n".join(
            f"[{index}] {chunk['content']}"
            for index, chunk in enumerate(chunks, start=1)
        )

        prompt = f"""Bạn là trợ lý hỏi đáp pháp lý dựa trên truy xuất ngữ cảnh.
Chỉ sử dụng thông tin có trong phần Context để trả lời.
Luôn trả lời bằng tiếng Việt, ngắn gọn, trực diện, tối đa 4 ý hoặc khoảng 120 từ.
Không nhắc lại từ "Context", "Question", "Constraint", không viết phân tích, không hiển thị suy luận nội bộ, không viết nháp, không tự đánh giá câu trả lời.
Nếu câu hỏi mang tính khái quát như "luật này là gì", "luật này nói về gì", "nội dung chính là gì", hãy tóm tắt phạm vi nội dung hoặc các ý chính có thể suy ra trực tiếp từ Context.
Chỉ trả lời "Tôi không có đủ thông tin trong ngữ cảnh để trả lời." khi Context thật sự không đủ dữ kiện để trả lời ở mức khái quát hoặc cụ thể.
Nếu phù hợp, hãy nêu điều luật hoặc tiêu đề liên quan một cách ngắn gọn.
Hãy trả về đúng định dạng sau và không thêm gì khác:
FINAL_ANSWER:
<câu trả lời ngắn gọn>

Context:
{context}

Question: {question}

Answer:"""

        return self.llm_fn(prompt)
