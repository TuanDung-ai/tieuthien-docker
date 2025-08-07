import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

MODEL_NAME = "openai/gpt-3.5-turbo"
MAX_TOKENS = 400
TEMPERATURE = 0.6

PORT = int(os.getenv("PORT", 8080))
