from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import ExitBackCallbackData, AdsCallbackData


def get_confirmed_kb(id_: int, type_: str, index: int):
    buttons = [
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=AdsCallbackData(
                    action="confirmed", id=id_, index=index, type_=type_
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=AdsCallbackData(
                    action="unconfirmed", id=id_, index=index, type_=type_
                ).pack(),
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