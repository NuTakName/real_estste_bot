from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from cached_data.cached_flat import CachedFlat
from callbacks import TypeRealtyCallbackData, PaginatorCallbackData
from core import User
from keyboards.main_keyboard import get_main_kb
from keyboards.paginator_keyboard import get_paginator_kb
from utilits import (
    push_message_to_state,
    clear_dialog,
    send_media_group_and_push_messages_to_state,
    get_media_group,
    get_text_for_ads_mess
)

router = Router()

@router.callback_query(TypeRealtyCallbackData.filter(F.action.in_(["buy_flat", "rent_flat"])))
async def buy_or_rent_flat(
        callback: types.CallbackQuery,
        callback_data: TypeRealtyCallbackData,
        admin: bool,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    cached_flat = CachedFlat()
    action = "buy_flat" if callback_data.action == "buy_flat" else "rent_flat"
    flat = await cached_flat.get(action=action)
    if flat:
        media = get_media_group(data=flat)
        await send_media_group_and_push_messages_to_state(
            state=state, media=media, callback=callback, user=user
        )
        text = get_text_for_ads_mess(entity=flat, user=user)
        reply_markup = get_paginator_kb(id_=flat.id, action=callback_data.action, index=0)
    else:
        text = "На данный момент нет объявлений в этом разделе"
        reply_markup = get_main_kb(admin=admin)
    await push_message_to_state(
        await callback.message.answer(text=text, reply_markup=reply_markup),
        state=state
    )


@router.callback_query(PaginatorCallbackData.filter(
    F.action.in_(["buy_flat_previous", "rent_flat_previous", "buy_flat_next", "rent_flat_next"])))
async def show_owner_or_next_flat(
        callback: types.CallbackQuery,
        callback_data: PaginatorCallbackData,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    cached_flat = CachedFlat()
    if callback_data.action == "buy_flat_previous" or callback_data.action == "rent_flat_previous":
        flat = cached_flat.get_previous(action=callback_data.do, index=callback_data.index)
    else:
        flat = cached_flat.get_next(action=callback_data.do, index=callback_data.index)
    if flat:
        media = get_media_group(data=flat)
        await send_media_group_and_push_messages_to_state(
            state=state, media=media, callback=callback, user=user
        )
        text = get_text_for_ads_mess(entity=flat, user=user)
        reply_markup = get_paginator_kb(id_=flat.id, action=callback_data.do, index=callback_data.index+1)
        await push_message_to_state(
            await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )