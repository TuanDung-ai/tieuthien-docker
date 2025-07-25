import requests
import os

def get_ai_response(user_prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Thiết lập hệ thống phản hồi phong cách Thiên Cơ
    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là Thiên Cơ – một AI trợ lý cá nhân đáng tin cậy. "
                "Giọng điệu trầm ổn, chính xác, nhẹ nhàng, thỉnh thoảng có chút hài hước nhẹ. "
                "Luôn trả lời ngắn gọn, không quá 3 câu. Cuối mỗi phản hồi, đưa ra gợi ý tiếp theo phù hợp. "
                "Ví dụ gợi ý: 'Bạn cần ghi nhớ điều gì?', 'Thiên Cơ có thể nhắc lịch, tâm sự hoặc kể chuyện...', "
                "'Cần hỗ trợ gì thêm không?' "
                "Nếu không rõ câu hỏi, hãy hỏi lại nhẹ nhàng. Không trả lời quá dài hay lan man."
            )
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    payload = {
        "model": "openai/gpt-3.5-turbo",  # Dùng GPT Free qua OpenRouter
        "messages": messages,
        "temperature": 0.6,  # Trả lời chính xác, giữ phong cách ổn định
        "max_tokens": 400
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Lỗi AI:", e)
        return "Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."
