from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks import ClearStateCallbackData


def get_clear_state_kb():
    buttons = [
        [
            InlineKeyboardButton(
                text="Отменить",
                callback_data=ClearStateCallbackData(action="clear_state").pack(),
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard