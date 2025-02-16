from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks import ExitBackCallbackData, PaginatorCallbackData


def get_paginator_kb(id_: int, action: str, index: int):
    buttons = [
        [
            InlineKeyboardButton(
                text="Предыдущее объявление",
                callback_data=PaginatorCallbackData(
                    action=f'{action}_previous',
                    id=id_,
                    do=action,
                    index=index
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Следующее объявление",
                callback_data=PaginatorCallbackData(
                    action=f"{action}_next",
                    id=id_,
                    do=action,
                    index=index
                ).pack(),
            ),
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