from aiogram.fsm.context import FSMContext

from cached_data.cached_unconfirmed_ads import UnconfirmedAds
from callbacks import AdsCallbackData
from aiogram import Router, F, types

from core import AdsType, RejectedAds
from core.users.models import User
from keyboards.confirmed_keyboard import get_confirmed_kb
from keyboards.main_keyboard import get_main_kb
from main import send_notification_about_rejected_or_confirmed_ads
from states import RejectAds
from utilits import (
    clear_dialog,
    get_data,
    get_text_for_ads_message,
    send_media_group_and_push_messages_to_state,
    push_message_to_state
)


router = Router()



@router.callback_query(AdsCallbackData.filter(F.action.in_(["confirmed", "unconfirmed"])))
async def confirmed_or_unconfirmed_ads(
        callback: types.CallbackQuery,
        callback_data: AdsCallbackData,
        state: FSMContext,
        user: User
):
    await clear_dialog(state=state)
    data = await get_data(id_=callback_data.id, type_=callback_data.type_)
    if callback_data.action == "confirmed":
        if data:
            await data.confirmed_ads()
        send_notification_about_rejected_or_confirmed_ads.apply_async(args=(
            data.user_id, None, None, None, True))
        unconfirmed_ads = UnconfirmedAds()
        unconfirmed_ads.remove_ads()
        new_data = await unconfirmed_ads.get_data()
        if not new_data:
            await push_message_to_state(
                await callback.message.answer(
                    text="Больше нет объявлений на проверку", reply_markup=get_main_kb(admin=True)),
                state
            )
            return
        text, type_, media = get_text_for_ads_message(data=new_data, user=user)
        await send_media_group_and_push_messages_to_state(state=state, media=media, callback=callback, user=user)
        reply_markup = get_confirmed_kb(id_=new_data.id, type_=type_, index= callback_data.index + 1
        )
        await push_message_to_state(
            message=await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )
    else:
        await push_message_to_state(
            await callback.message.answer(text="Укажите причину отклонения уведомления"),
            state=state
        )
        await state.set_state(RejectAds.reason)
        await state.update_data(
            ads_name=data.info,
            types_=callback_data.type_,
            current_id=data.id,
            owner_uid=data.user_id,
            index=callback_data.index
        )



@router.message(RejectAds.reason)
async def send_reason(message: types.Message, state: FSMContext, user: User):
    await clear_dialog(state=state)
    data = await state.get_data()
    owner_uid = data.get("owner_uid")
    types_ = data.get("types_")
    id_ = data.get("current_id")
    ads_name = data.get("ads_name")
    flat_id = None
    house_id = None
    garage_id = None
    if types_ == AdsType.flat:
        type_ = AdsType.flat
        flat_id = id_
    elif types_ == AdsType.house:
        type_ = AdsType.house
        house_id = id_
    else:
        garage_id = id_
        type_ = AdsType.garage
    owner = await User.get(owner_uid)
    rejected_ads = RejectedAds(
        user_id=owner.id,
        type_=type_,
        flat_id=flat_id,
        house_id=house_id,
        garage_id=garage_id,
        reason=str(message.text)
    )
    await rejected_ads.add()
    send_notification_about_rejected_or_confirmed_ads.apply_async(args=(
        owner.user_id, user.username, str(message.text), ads_name
    ))
    unconfirmed_ads = UnconfirmedAds()
    unconfirmed_ads.remove_ads()
    new_data = await unconfirmed_ads.get_data()
    await message.delete()
    if new_data:
        text, type_, media = get_text_for_ads_message(data=new_data, user=user)
        await send_media_group_and_push_messages_to_state(state=state, media=media, callback=message)
        reply_markup = get_confirmed_kb(id_=new_data.id, type_=type_, index=data.get("index", 0) + 1)
        await push_message_to_state(
            await message.answer(text=text, reply_markup=reply_markup),
            state=state
        )
    else:
        await push_message_to_state(
            await message.answer(
                text="Больше нет объявлений на проверку", reply_markup=get_main_kb(admin=True)),
            state
        )
        return