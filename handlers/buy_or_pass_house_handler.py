from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from cached_data.cached_house import CachedHouse
from callbacks import TypeRealtyCallbackData, PaginatorCallbackData
from core import User
from keyboards.main_keyboard import get_main_kb
from keyboards.paginator_keyboard import get_paginator_kb
from utilits import (
    clear_dialog,
    get_media_group,
    send_media_group_and_push_messages_to_state,
    push_message_to_state,
    get_text_for_ads_mess
)

router = Router()


@router.callback_query(TypeRealtyCallbackData.filter(F.action.in_(["buy_house", "rent_house"])))
async def buy_or_rent_house(
        callback: types.CallbackQuery,
        callback_data: TypeRealtyCallbackData,
        admin: bool,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    cached_house = CachedHouse()
    action = "buy_house" if callback_data.action == "buy_house" else "rent_house"
    house = await cached_house.get(action=action)
    if house:
        media = get_media_group(data=house)
        await send_media_group_and_push_messages_to_state(
            state=state, media=media, callback=callback, user=user
        )
        text = get_text_for_ads_mess(entity=house, user=user)
        reply_markup = get_paginator_kb(id_=house.id, action=callback_data.action, index=0)
    else:
        text = "На данный момент нет объявлений в этом разделе"
        reply_markup = get_main_kb(admin=admin)
    await push_message_to_state(
        await callback.message.answer(text=text, reply_markup=reply_markup),
        state=state
    )


@router.callback_query(PaginatorCallbackData.filter(
    F.action.in_(["buy_house_previous", "rent_house_previous", "buy_house_next", "rent_house_next"])))
async def show_owner_or_next_house(
        callback: types.CallbackQuery,
        callback_data: PaginatorCallbackData,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    cached_house = CachedHouse()
    if callback_data.action == "buy_house_previous" or callback_data.action == "rent_house_previous":
        house = cached_house.get_previous(action=callback_data.do, index=callback_data.index)
    else:
        house = cached_house.get_next(action=callback_data.do, index=callback_data.index)
    if house:
        media = get_media_group(data=house)
        await send_media_group_and_push_messages_to_state(
            state=state, media=media, callback=callback, user=user
        )
        text = get_text_for_ads_mess(entity=house, user=user)
        reply_markup = get_paginator_kb(id_=house.id, action=callback_data.do, index=callback_data.index+1)
        await push_message_to_state(
            await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )