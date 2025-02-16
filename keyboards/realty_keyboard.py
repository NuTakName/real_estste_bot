from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import TypeRealtyCallbackData, ExitBackCallbackData


def get_type_realty_kb(action: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="Квартира",
                callback_data=TypeRealtyCallbackData(action=f"{action}_flat").pack(),
            ),
            InlineKeyboardButton(
                text="Дом",
                callback_data=TypeRealtyCallbackData(action=f"{action}_house").pack(),
            ),
            InlineKeyboardButton(
                text="Гараж",
                callback_data=TypeRealtyCallbackData(action=f"{action}_garage").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ExitBackCallbackData(action="exit_back").pack(),
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard