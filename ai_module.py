import os
import requests

# Lấy key API từ biến môi trường
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# Hàm định dạng phản hồi AI – chuẩn Thiên Cơ
def format_reply(ai_content):
    return (
        "🌀 Thiên Cơ phản hồi:\n\n"
        f"{ai_content.strip()}\n\n"
        "✨ Bạn muốn ghi nhớ, xem lịch, hay thư giãn?"
    )

# Hàm phản hồi AI qua OpenRouter – đã tối ưu
def get_ai_response(user_prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là Thiên Cơ – một AI trợ lý cá nhân đáng tin cậy. "
                "Giọng điệu trầm ổn, chính xác, nhẹ nhàng, thỉnh thoảng có chút hài hước nhẹ. "
                "Luôn trả lời ngắn gọn, không quá 3 câu. Cuối mỗi phản hồi, đưa ra gợi ý tiếp theo phù hợp. "
                "Ví dụ: 'Bạn cần ghi nhớ điều gì?', 'Thiên Cơ có thể nhắc lịch, tâm sự hoặc kể chuyện...'. "
                "Nếu không rõ câu hỏi, hãy hỏi lại nhẹ nhàng. Không trả lời quá dài hay lan man."
            )
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
        return "🌀 Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé.\n✨ Bạn muốn thử lại, ghi nhớ, hay xem lịch?"
