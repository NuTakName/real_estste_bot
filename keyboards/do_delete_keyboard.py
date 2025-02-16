from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks import AdsCallbackData


def get_delete_kb(id_: int, type_: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="Да",
                callback_data=AdsCallbackData(action="yes", id=id_, type_=type_).pack(),
            ),
            InlineKeyboardButton(
                text="Нет",
                callback_data=AdsCallbackData(action="no", id=id_, type_=type_).pack(),
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard