from sys import prefix

from aiogram.filters.callback_data import CallbackData


class MainCallbackData(CallbackData, prefix="main_"):
    action: str


class TypeRealtyCallbackData(CallbackData, prefix="type_realty_"):
    action: str

class ExitBackCallbackData(CallbackData, prefix="exit_back_"):
    action: str

class ClearStateCallbackData(CallbackData, prefix="clear_state_"):
    action: str

class PaginatorCallbackData(CallbackData, prefix="paginator_flat"):
    action: str
    id: int
    do: str
    index: int | None = None

class AdsCallbackData(CallbackData, prefix="my_ads"):
    action: str
    id: int
    type_: str
    index: int | None = None

class ChangeCallbackData(CallbackData, prefix="change_ads"):
    action:str
    id: int
    type_: str

class ConfirmSaveEstateCallbackData(CallbackData, prefix="confirm_save_estate"):
    action: str


class SearchAdsCallbackData(CallbackData, prefix="search_ads"):
    action: str


class SettingsCallbackData(CallbackData, prefix="settings"):
    action: str


class CurrencyCallbackData(CallbackData, prefix="currency"):
    type_: str