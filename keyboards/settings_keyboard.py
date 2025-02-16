from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import SettingsCallbackData, ExitBackCallbackData, CurrencyCallbackData


def get_settings_kb(notification: bool) -> InlineKeyboardMarkup:
    text = "Отключить уведомления" if notification else "Включить уведомления"
    button = [
        [
            InlineKeyboardButton(
                text=text, callback_data=SettingsCallbackData(action="change_notification").pack()
            ),
            InlineKeyboardButton(
                text="Изменить валюту", callback_data=SettingsCallbackData(action="change_currency").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ExitBackCallbackData(action="exit_back").pack(),
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard



def get_change_currency_kb() -> InlineKeyboardMarkup:
    currency = ["RUB", "EUR", "USD"]
    button = [[]]
    for c in currency:
        button[0].append(
            InlineKeyboardButton(text=c, callback_data=CurrencyCallbackData(type_=c).pack())
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard
