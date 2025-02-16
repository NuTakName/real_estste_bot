from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_me_contact_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, resize_keyboard=True)
    return keyboard

