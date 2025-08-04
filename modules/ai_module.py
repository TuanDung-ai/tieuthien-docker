import os
import requests
from memory.memory_manager import get_memory  # Lấy ghi nhớ từ bộ nhớ hợp nhất (SQLite + Supabase)

# === API KEY OpenRouter ===
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def format_reply(ai_content):
    """Định dạng phản hồi từ AI, kèm câu gợi ý."""
    return (
        "🌀 Thiên Cơ phản hồi:\n\n"
        f"{ai_content.strip()}\n\n"
        "✨ Bạn muốn ghi nhớ, xem lịch, hay thư giãn?"
    )

async def get_ai_response_with_memory(user_id, user_prompt):
    """
    Tạo phản hồi AI có tích hợp ghi nhớ người dùng.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    # === Tạo ngữ cảnh từ ghi nhớ gần nhất ===
    memories = get_memory(user_id)
    memory_context = ""
    if memories:
        # Sắp xếp theo thời gian nếu cần; lấy 5 ghi nhớ cuối cùng
        for mem in memories[-5:]:
            note_type = mem.get('note_type', 'khác')
            content = mem.get('content', '')
            memory_context += f"- Ghi nhớ ({note_type}): {content}\n"

    # === Tạo system prompt ===
    system_message = (
        "Bạn là Tiểu Thiên – một AI trợ lý cá nhân đáng tin cậy. "
        "Giọng điệu trầm ổn, chính xác, nhẹ nhàng, đôi lúc hài hước. "
        "Luôn trả lời ngắn gọn (dưới 3 câu), không lan man. "
        "Luôn gợi ý tiếp theo sau mỗi phản hồi: 'Ghi nhớ điều gì?', 'Xem lịch?', 'Thư giãn?'. "
        "Nếu không rõ câu hỏi, hãy hỏi lại nhẹ nhàng.\n\n"
        "Đây là một số ghi nhớ của chủ nhân:\n"
        f"{memory_context}"
    )

    # === Tạo payload gửi OpenRouter ===
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": "openai/gpt-3.5-turbo",  # Có thể thay đổi model nếu cần
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 400
    }

    # === Gửi yêu cầu và xử lý phản hồi ===
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        ai_reply_raw = data["choices"][0]["message"]["content"]
        return format_reply(ai_reply_raw)
    except Exception as e:
        print("Lỗi gọi API OpenRouter:", e)
        return "🌀 Tiểu Thiên gặp trục trặc nhẹ... thử lại sau nhé.\n✨ Bạn muốn thử lại, ghi nhớ, hay xem lịch?"
