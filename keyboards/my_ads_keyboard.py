from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks import ExitBackCallbackData, AdsCallbackData, ChangeCallbackData


def get_my_ads_kb(id_: int, type_: str, index: int):
    buttons = [
        [InlineKeyboardButton(text="Предыдущее объявление", callback_data=AdsCallbackData(
            action="previous", id=id_, type_=type_, index=index).pack(),
            ),
        InlineKeyboardButton(text="Следующее объявление", callback_data=AdsCallbackData(
            action="next", id=id_, type_=type_, index=index).pack())
        ],
        [InlineKeyboardButton(text="Удалить", callback_data=AdsCallbackData(
            action="delete", id=id_, type_=type_).pack()),
        InlineKeyboardButton(text="Изменить объявление", callback_data=AdsCallbackData(
            action="change_ads", id=id_, type_=type_).pack())],
        [InlineKeyboardButton(text="Назад", callback_data=ExitBackCallbackData(action="exit_back").pack())]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



def get_change_kb(id_: int, type_: str) -> InlineKeyboardMarkup:
    button = [
        [
            InlineKeyboardButton(text="Город", callback_data=ChangeCallbackData(
                action="change_city", id=id_, type_=type_).pack()),
            InlineKeyboardButton(text="Район", callback_data=ChangeCallbackData(
                action="change_district", id=id_, type_=type_).pack()),
            InlineKeyboardButton(text="Информацию", callback_data=ChangeCallbackData(
                action="change_info", id=id_, type_=type_
            ).pack())
        ],
        [
            InlineKeyboardButton(text="Цену", callback_data=ChangeCallbackData(
                action="change_price", id=id_, type_=type_).pack()),
            InlineKeyboardButton(text="Адрес", callback_data=ChangeCallbackData(
                action="change_address", id=id_, type_=type_).pack())
        ]
    ]
    if type_ == 'flat' or type_ == "house":
        button.append(
            [
                InlineKeyboardButton(text="Количество комнат", callback_data=ChangeCallbackData(
                    action="change_rooms", id=id_, type_=type_).pack()),
                InlineKeyboardButton(text="Площадь", callback_data=ChangeCallbackData(
                    action="change_area", id=id_, type_=type_).pack())
            ]
        )
    if type_ == "flat":
        button.append(
            [
                InlineKeyboardButton(text="Этаж", callback_data=ChangeCallbackData(
                    action="change_floor", id=id_, type_=type_).pack())
            ]
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard
