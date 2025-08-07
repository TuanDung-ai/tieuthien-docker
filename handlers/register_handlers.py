# handlers/register_handlers.py
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.commands import (
    cmd_ghi_nho, cmd_xem_nho, cmd_xoa_nho,
    cmd_xoa_tatca, cmd_tro_giup
)
from handlers.message_handler import handle_message
from modules.memory_manager import handle_callback_query


def register_handlers(app: Application):
    app.add_handler(CommandHandler("ghi_nho", cmd_ghi_nho))
    app.add_handler(CommandHandler("xem_nho", cmd_xem_nho))
    app.add_handler(CommandHandler("xoa_nho", cmd_xoa_nho))
    app.add_handler(CommandHandler("xoa_tatca", cmd_xoa_tatca))
    app.add_handler(CommandHandler("tro_giup", cmd_tro_giup))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
