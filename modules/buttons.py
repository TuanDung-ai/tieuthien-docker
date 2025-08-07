from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📖 Xem nhớ", callback_data='view')
        ],
        [
            InlineKeyboardButton("🗑️ Xóa hết", callback_data='clear_all')
        ]
    ])

def get_note_type_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Tâm sự", callback_data='type_tamsu'),
            InlineKeyboardButton("⏰ Nhắc nhở", callback_data='type_nhacnho')
        ],
        [
            InlineKeyboardButton("💡 Ý tưởng", callback_data='type_ytuong'),
            InlineKeyboardButton("📂 Cá nhân", callback_data='type_canhan')
        ]
    ])
