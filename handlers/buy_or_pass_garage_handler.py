from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cached_data.cached_garage import CachedGarage
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

@router.callback_query(TypeRealtyCallbackData.filter(F.action.in_(["buy_garage", "rent_garage"])))
async def buy_or_rent_garage(
        callback: types.CallbackQuery,
        callback_data: TypeRealtyCallbackData,
        admin: bool,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    cached_house = CachedGarage()
    action = "buy_garage" if callback_data.action == "buy_garage" else "rent_garage"
    garage = await cached_house.get(action=action)
    if garage:
        media = get_media_group(data=garage)
        await send_media_group_and_push_messages_to_state(
            state=state, media=media, callback=callback, user=user
        )
        text = get_text_for_ads_mess(entity=garage, user=user)
        reply_markup = get_paginator_kb(id_=garage.id, action=callback_data.action, index=0)
    else:
        text = "На данный момент нет объявлений в этом разделе"
        reply_markup = get_main_kb(admin=admin)
    await push_message_to_state(
        await callback.message.answer(text=text, reply_markup=reply_markup),
        state=state
    )

@router.callback_query(PaginatorCallbackData.filter(
    F.action.in_(["buy_garage_previous", "rent_garage_previous", "buy_garage_next", "rent_garage_next"])))
async def show_owner_or_next_garage(
        callback: types.CallbackQuery,
        callback_data: PaginatorCallbackData,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    cached_garage = CachedGarage()
    if callback_data.action == "buy_garage_previous" or callback_data.action == "rent_garage_previous":
        garage = cached_garage.get_previous(action=callback_data.do, index=callback_data.index)
    else:
        garage = cached_garage.get_next(action=callback_data.do, index=callback_data.index)
    if garage:
        media = get_media_group(data=garage)
        await send_media_group_and_push_messages_to_state(
            state=state, media=media, callback=callback, user=user
        )
        text = get_text_for_ads_mess(entity=garage, user=user)
        reply_markup = get_paginator_kb(id_=garage.id, action=callback_data.do, index=callback_data.index + 1)
        await push_message_to_state(
            await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )