# handlers/register_handlers.py
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from .start import start_command, help_command
from modules.memory_manager import handle_message, handle_callback_query

def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

