import requests
import os

def get_ai_response(user_prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "Bạn là Thiên Cơ – AI trợ lý cá nhân, trầm ổn – chính xác – hài hước nhẹ. Trả lời ngắn gọn, có gợi ý."},
        {"role": "user", "content": user_prompt}
    ]
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 400
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Lỗi AI:", e)
        return "Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."
