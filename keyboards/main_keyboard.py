from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import MainCallbackData, SearchAdsCallbackData


def get_main_kb(admin: bool = False):
    buttons_line_one = [
        InlineKeyboardButton(
            text="Купить",
            callback_data=MainCallbackData(action="buy").pack(),
        ),
        InlineKeyboardButton(
            text="Арендовать",
            callback_data=MainCallbackData(action="rent").pack(),
        )
    ]
    buttons_line_two = [
        InlineKeyboardButton(
            text="Продать",
            callback_data=MainCallbackData(action="sell").pack(),
        ),
        InlineKeyboardButton(
            text="Сдать",
            callback_data=MainCallbackData(action="pass").pack(),
        )
    ]
    buttons_line_three = [
        InlineKeyboardButton(
            text="Мои объявления",
            callback_data=MainCallbackData(action="my_ads").pack(),
        ),
        InlineKeyboardButton(
            text="Настройки",
            callback_data=MainCallbackData(action="open_settings").pack()
        )
    ]
    buttons = [buttons_line_one, buttons_line_two, buttons_line_three]
    if admin:
        buttons_for_admin = [
            InlineKeyboardButton(
                text="Объявления на проверку",
                callback_data=MainCallbackData(action="verification_ads").pack(),
            ),
            InlineKeyboardButton(
                text="Найти объявления",
                callback_data=SearchAdsCallbackData(action="find_ads").pack()
            )
        ]
        buttons.append(buttons_for_admin)
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

