from typing import Union
from aiogram import types
from aiogram.exceptions import DetailedAiogramError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InputMediaPhoto, FSInputFile, InputFile

from cached_data.cached_unconfirmed_ads import UnconfirmedAds
from core import User, UserSetting
from core.garage.models import Garage
from core.houses.models import House
from core.flats.models import Flat
from loguru import logger

from currency_converter import get_amount_for_ads
from states import ChangeState


def get_text_for_ads_message(data: Union[Flat, Garage, House], user: User) -> tuple[str, str, list]:
    if isinstance(data, Garage):
        text = get_text_for_ads_mess(entity=data, user=user)
        type_ = "garage"
    elif isinstance(data, House):
        text = get_text_for_ads_mess(entity=data, user=user)
        type_ = "house"
    else:
        text = get_text_for_ads_mess(entity=data, user=user)
        type_ = "flat"
    media = get_media_group(data=data)
    return text, type_, media


def get_media_group(data: Union[Flat, Garage, House]) -> list:
    media = []
    for photo in data.photos:
        if ".jpg" in photo or ".svg" in photo or ".png" in photo:
            media.append(InputMediaPhoto(media=FSInputFile(path=photo)))
        else:
            media.append(InputMediaPhoto(media=photo))
    return media


async def send_media_group_and_push_messages_to_state(
        state: FSMContext,
        media: list,
        callback: Union[types.CallbackQuery, types.Message],
        user: User
):
    chat_id = callback.chat.id if isinstance(callback, types.Message) else callback.message.chat.id
    try:
        await push_media_group(callback, chat_id, state, media)
    except TelegramBadRequest as e:
        logger.warning(e)
        unconfirmed_ads = UnconfirmedAds()
        unconfirmed_ads.remove_ads()
        data = await unconfirmed_ads.get_data()
        text, type_, media = get_text_for_ads_message(data=data, user=user)
        await push_media_group(callback, chat_id, state, media)


async def push_media_group(
        callback: Union[types.CallbackQuery, types.Message],
        chat_id: int,
        state: FSMContext,
        media: list
):
    messages = await callback.bot.send_media_group(
        chat_id=chat_id,
        media=media
    )
    for mess in messages:
        await push_message_to_state(message=mess, state=state)



async def push_message_to_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages = data.get("messages", [])
    if messages is None:
        messages = []
    messages.append(message)
    await state.update_data(messages=messages)
    return message


async def clear_dialog(state: FSMContext):
    data = await state.get_data()
    messages: list[types.Message] = data.get("messages", [])
    for mess in messages:
        try:
            await mess.bot.delete_message(chat_id=mess.chat.id, message_id=mess.message_id)
        except DetailedAiogramError as e:
            pass


async def get_data(type_: str, id_: int):
    if type_ == "garage":
        data = await Garage.get_by_id(garage_id=id_)
    elif type_ == "house":
        data = await House.get_by_id(house_id=id_)
    else:
        data = await Flat.get_by_id(flat_id=id_)
    return data


def get_text_for_ads_mess(entity: Union[Flat, House, Garage], user: User) -> str:
    if isinstance(entity, Flat):
        type_entity = "квартира"
        rooms = "Не указано" if not entity.rooms else entity.rooms
        general_area = "Не указано" if not entity.the_general_area else f"{entity.the_general_area} кв.м"
        floor = "Не указано" if not entity.floor else entity.floor
        additional_info = f"Количество комнат: {rooms}\nОбщая площадь: {general_area}\nЭтаж: {floor}"
    elif isinstance(entity, House):
        type_entity = "дом"
        rooms = "Не указано" if not entity.rooms else entity.rooms
        general_area = "Не указано" if not entity.the_general_area else f"{entity.the_general_area} кв.м"
        additional_info = f"Количество комнат: {rooms}\nОбщая площадь: {general_area}"
    else:
        type_entity = "гараж"
        additional_info = ""
    rent = f"Сдается {type_entity}" if entity.rent else f"В продаже {type_entity}"
    district = "Не указано" if not entity.district else entity.district
    price = "Договорная" if not entity.price else get_amount_for_ads(
        user_currency=user.user_setting.get("currency"), amount=float(entity.price)
    )
    contact = f"@{entity.user_name}" if entity.user_name else entity.phone
    info = "Не указано" if not entity.info else entity.info
    full_address = "Не указано" if not entity.address else entity.address
    text = (f'{rent}\n'
            f'Город: {entity.city}\n'
            f'Район: {district}\n'
            f'Полный адрес: {full_address}\n'
            f'Цена: {price}\n'
            f'Дополнительная информация: {info}\n'
            f'Продавец: {contact if contact else user.first_name}\n'
            f'{additional_info}')
    return text.strip()


async def get_photos(state: FSMContext) -> list[str]:
    data = await state.get_data()
    photos = [str(data.get("photo1")),str(data.get("photo2")), str(data.get("photo3"))]
    return photos


async def get_text_for_user_settings(user_id: int) -> str:
    user_settings = await UserSetting.get_by_user_id(uid=user_id)
    currency = user_settings.currency.value
    notification = "Включены" if user_settings.notification else "Отключены"
    text = f"Уведомления: {notification}\n Валюта: {currency}"
    return text



def get_state_and_text(change: str) -> tuple[State, str]:
    if change == "change_city":
        new_state = ChangeState.city
        text = "Введите новое название города"
    elif change == "change_district":
        new_state = ChangeState.district
        text = "Введите новый район"
    elif change == "change_info":
        new_state = ChangeState.info
        text = "Введите информацию о недвижимости"
    elif change == "change_price":
        new_state = ChangeState.price
        text = "Введите новую цену"
    elif change == "change_address":
        new_state = ChangeState.address
        text = "Введите новый адрес"
    elif change == "change_rooms":
        new_state = ChangeState.number_of_rooms
        text = "Введите количество комнат"
    elif change == "change_area":
        new_state = ChangeState.number_of_rooms
        text = "Введите площадь"
    else:
        new_state = ChangeState.floor
        text = "На каком этаже находится квартира?"
    return new_state, text


async def get_ads_by_id_and_type(state: FSMContext) -> Union["Flat", "Garage", "House"]:
    data = await state.get_data()
    type_ = data.get("type_")
    id_ = data.get("id_")
    if type_ == "flat":
        data = await Flat.get_by_id(id_)
    elif type_ == "house":
        data = await House.get_by_id(id_)
    else:
        data = await Garage.get_by_id(id_)
    return data
