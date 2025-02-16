from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from callbacks import SettingsCallbackData, CurrencyCallbackData
from core import User, UserSetting, CurrencyType
from keyboards.settings_keyboard import get_settings_kb, get_change_currency_kb
from utilits import clear_dialog, push_message_to_state, get_text_for_user_settings

router = Router()



@router.callback_query(SettingsCallbackData.filter())
async def handle_change_settings(
        callback: types.CallbackQuery,
        state: FSMContext,
        user: User,
        callback_data: SettingsCallbackData,
):
    await clear_dialog(state=state)
    if callback_data.action == "change_notification":
        notification = user.user_setting.get("notification")
        user_settings = await UserSetting.get_by_user_id(uid=user.user_id)
        user_settings.notification = not notification
        user_settings = await user_settings.update()
        text = await get_text_for_user_settings(user_id=user.user_id)
        reply_markup = get_settings_kb(notification=user_settings.notification)
        await push_message_to_state(
            await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )
    else:
        reply_markup = get_change_currency_kb()
        await push_message_to_state(
            await callback.message.answer(text="Выберите новую валюту", reply_markup=reply_markup),
            state=state
        )


@router.callback_query(CurrencyCallbackData.filter())
async def change_currency(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: CurrencyCallbackData,
        user: User
):
    await clear_dialog(state=state)
    user_settings = await UserSetting.get_by_user_id(uid=user.user_id)
    currency = callback_data.type_
    user_settings.currency = currency
    await user_settings.update()
    text = await get_text_for_user_settings(user_id=user.user_id)
    reply_markup = get_settings_kb(notification=user.user_setting.get("notification"))
    await push_message_to_state(
        await callback.message.answer(text=text, reply_markup=reply_markup),
        state=state
    )




