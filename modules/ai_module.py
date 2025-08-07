# modules/ai_module.py
import os
import requests
from modules.memory_manager import get_memory
from config import OPENROUTER_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE


def format_reply(ai_content):
    return (
        "🌀 Thiên Cơ phản hồi:\n\n"
        f"{ai_content.strip()}\n\n"
        "✨ Bạn muốn ghi nhớ điều gì tiếp theo?"
    )


async def get_ai_response_with_memory(user_id, user_prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    # === Tạo ngữ cảnh từ ghi nhớ gần nhất ===
    memories = get_memory(user_id)
    memory_context = ""
    if memories:
        for mem in memories[-5:]:
            note_type = mem.get('note_type', 'khác')
            content = mem.get('content', '')
            memory_context += f"- ({note_type}) {content}\n"

    # === Prompt hệ thống nâng cấp ===
    system_message = (
        "Bạn là Thiên Cơ – trợ lý AI cá nhân của người dùng. "
        "Luôn nói chuyện ngắn gọn, trầm tĩnh, đúng trọng tâm. "
        "Nếu có ghi nhớ liên quan, hãy sử dụng để trả lời hợp ngữ cảnh. "
        "Không lan man. Kết thúc bằng câu hỏi như 'Ghi nhớ gì tiếp theo?' hoặc 'Muốn xem lại ghi chú không?'.\n\n"
        f"Ghi nhớ của người dùng:\n{memory_context}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        ai_reply_raw = data["choices"][0]["message"]["content"]
        return format_reply(ai_reply_raw)
    except Exception as e:
        print("Lỗi gọi API OpenRouter:", e)
        return "🌀 Thiên Cơ gặp trục trặc nhẹ... Thử lại sau nhé."


# Đã loại bỏ: - mọi dòng gợi ý 'thư giãn'
#             - mọi nội dung 'calendar', 'thugian' không còn tồn tại
