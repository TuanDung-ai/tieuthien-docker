# modules/ai_module.py
import os
import requests
from memory.memory_manager import get_memory # Import hàm get_memory từ memory_manager

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def format_reply(ai_content):
    """Định dạng phản hồi từ AI."""
    return (
        "🌀 Thiên Cơ phản hồi:\n\n"
        f"{ai_content.strip()}\n\n"
        "✨ Bạn muốn ghi nhớ, xem lịch, hay thư giãn?"
    )

async def get_ai_response_with_memory(user_id, user_prompt):
    """
    Hàm này lấy phản hồi từ AI, có tích hợp dữ liệu ghi nhớ của người dùng.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    # Bắt đầu lấy ghi nhớ từ bộ nhớ của chủ nhân
    # Tiểu Thiên sẽ lấy 5 ghi nhớ gần nhất của chủ nhân để làm ngữ cảnh
    memories = get_memory(user_id)
    memory_context = ""
    if memories:
        for mem in memories[-5:]: # Lấy 5 ghi nhớ gần nhất
            memory_context += f"- Ghi nhớ ({mem['note_type']}): {mem['content']}\n"
    
    # Bổ sung ghi nhớ vào prompt để AI hiểu rõ hơn
    system_message = (
        "Bạn là Tiểu Thiên – một AI trợ lý cá nhân đáng tin cậy. "
        "Giọng điệu trầm ổn, chính xác, nhẹ nhàng, thỉnh thoảng có chút hài hước nhẹ. "
        "Luôn trả lời ngắn gọn, không quá 3 câu. Cuối mỗi phản hồi, đưa ra gợi ý tiếp theo phù hợp. "
        "Ví dụ: 'Bạn cần ghi nhớ điều gì?', 'Tiểu Thiên có thể nhắc lịch, tâm sự hoặc kể chuyện...'. "
        "Nếu không rõ câu hỏi, hãy hỏi lại nhẹ nhàng. Không trả lời quá dài hay lan man.\n\n"
        "Đây là một số ghi nhớ của chủ nhân (dùng để trả lời tốt hơn):\n"
        f"{memory_context}"
    )

    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 400
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        ai_raw_reply = data["choices"][0]["message"]["content"]
        return format_reply(ai_raw_reply)
    except Exception as e:
        print("Lỗi AI:", e)
        return "🌀 Tiểu Thiên gặp trục trặc nhẹ... thử lại sau nhé.\n✨ Bạn muốn thử lại, ghi nhớ, hay xem lịch?"
