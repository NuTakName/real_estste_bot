
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram import types
from aiogram.fsm.context import FSMContext

from cached_data.cached_my_ads import CachedAds
from cached_data.cached_unconfirmed_ads import UnconfirmedAds
from callbacks import MainCallbackData, ExitBackCallbackData
from core import User
from keyboards.contact_keyboard import get_me_contact_kb
from keyboards.main_keyboard import get_main_kb
from keyboards.my_ads_keyboard import get_my_ads_kb
from keyboards.realty_keyboard import get_type_realty_kb
from keyboards.confirmed_keyboard import get_confirmed_kb
from keyboards.settings_keyboard import get_settings_kb
from utilits import (
    get_text_for_ads_message,
    send_media_group_and_push_messages_to_state,
    push_message_to_state,
    clear_dialog, get_text_for_user_settings
)

router = Router()

@router.message(CommandStart())
async def command_start(message: types.Message, user: User, admin: bool, state: FSMContext):
    await message.delete()
    if not user.phone:
        reply_markup = get_me_contact_kb()
        await push_message_to_state(
            await message.answer(text="Для завершения регистрации отправьте свой телефон", reply_markup=reply_markup),
            state=state
        )
    else:
        reply_markup = get_main_kb(admin=admin)
        mess = await message.answer(
            text=f"Привет, {user.get_full_name()}, я помогу тебе купить, продать или арендовать недвижимость",
            reply_markup=reply_markup
        )
        await push_message_to_state(message=mess, state=state)


@router.message(F.content_type == ContentType.CONTACT)
async def contact_handler(message: types.Message, state: FSMContext, user: User, admin: bool):
    await clear_dialog(state=state)
    user.phone = message.contact.phone_number
    await user.update()
    await message.delete()
    reply_markup = get_main_kb(admin=admin)
    mess = await message.answer(
        text=f"Привет, {user.get_full_name()}, я помогу тебе купить, продать или арендовать недвижимость",
        reply_markup=reply_markup
    )
    await push_message_to_state(message=mess, state=state)


@router.callback_query(MainCallbackData.filter())
async def buy(
        callback: types.CallbackQuery,
        callback_data: MainCallbackData,
        admin: bool,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    actions = ["buy", "sell", "rent", "pass"]
    if callback_data.action in actions:
        reply_markup = get_type_realty_kb(action=callback_data.action)
        await push_message_to_state(
            await callback.message.answer("Выберите тип недвижимости", reply_markup=reply_markup),
            state=state
        )
        return
    elif callback_data.action == "my_ads":
        cached_ads = CachedAds()
        data = await cached_ads.get(user_id=callback.from_user.id)
    elif callback_data.action == "open_settings":
        await handle_user_settings(user, callback, state)
        return
    else:
        unconfirmed_ads = UnconfirmedAds()
        data = await unconfirmed_ads.get_data()
    if data:
        text, type_, media = get_text_for_ads_message(data=data, user=user)
        await send_media_group_and_push_messages_to_state(state=state, media=media, callback=callback, user=user)
        if callback_data.action == "my_ads":
            reply_markup = get_my_ads_kb(id_=data.id, type_=type_, index=0)
        else:
            reply_markup = get_confirmed_kb(id_=data.id, type_=type_, index=0)
        await push_message_to_state(
            await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )
    else:
        reply_markup = get_main_kb(admin=admin)
        await push_message_to_state(
            await callback.message.answer(text="Нет объявлений в данной категории", reply_markup=reply_markup),
            state=state
        )



@router.callback_query(ExitBackCallbackData.filter(F.action == "exit_back"))
async def exit_back(callback: types.CallbackQuery, admin: bool, state: FSMContext):
    await clear_dialog(state=state)
    reply_markup = get_main_kb(admin=admin)
    await push_message_to_state(
        await callback.message.answer(text="Выберите действие", reply_markup=reply_markup),
        state=state
    )


async def handle_user_settings(user: User, callback: types.CallbackQuery, state: FSMContext):
    text = await get_text_for_user_settings(user_id=user.user_id)
    reply_markup = get_settings_kb(notification=user.user_setting.get("notification"))
    await push_message_to_state(
        await callback.message.answer(text=text, reply_markup=reply_markup),
        state=state
    )

