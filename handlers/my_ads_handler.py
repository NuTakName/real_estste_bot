
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from cached_data.cached_my_ads import CachedAds
from callbacks import AdsCallbackData, ChangeCallbackData
from core import User
from keyboards.do_delete_keyboard import get_delete_kb
from keyboards.main_keyboard import get_main_kb
from keyboards.my_ads_keyboard import get_my_ads_kb, get_change_kb
from states import ChangeState
from utilits import clear_dialog, send_media_group_and_push_messages_to_state, push_message_to_state, \
    get_text_for_ads_message, get_data, get_state_and_text, get_ads_by_id_and_type

router = Router()


@router.callback_query(AdsCallbackData.filter(F.action == "delete"))
async def send_confirmed_delete(callback: types.CallbackQuery, callback_data: AdsCallbackData, state: FSMContext):
    reply_markup = get_delete_kb(id_=callback_data.id, type_=callback_data.type_)
    await push_message_to_state(
        await callback.message.answer(text="Уверены, что хотите удалить объявление?", reply_markup=reply_markup),
        state=state
    )

@router.callback_query(AdsCallbackData.filter(F.action.in_(["yes", "no"])))
async def confirm_delete_ads(
        callback: types.CallbackQuery,
        callback_data: AdsCallbackData,
        state: FSMContext,
        admin: bool,
        user: User
):
    type_ = callback_data.type_
    id_ = callback_data.id
    await clear_dialog(state=state)
    if callback_data.action == "yes":
        data = await get_data(id_=id_, type_=type_)
        if data:
            await data.delete(type_)
    cached = CachedAds()
    new_data = await cached.get(user_id=callback.from_user.id)
    if new_data:
        text, type_, media = get_text_for_ads_message(data=new_data, user=user)
        index = 1 if callback_data.action == "yes" else 0
        reply_markup = get_my_ads_kb(
            id_=new_data.id,
            type_=type_,
            index=index
        )
        await send_media_group_and_push_messages_to_state(state=state, media=media, callback=callback)
        await push_message_to_state(
            await callback.message.answer(text=text, reply_markup=reply_markup),
            state=state
        )
    else:
        reply_markup = get_main_kb(admin=admin)
        await push_message_to_state(
            await callback.message.answer(
                text="У вас больше нет объявлений", reply_markup=reply_markup
            ),
            state=state
        )


@router.callback_query(AdsCallbackData.filter(F.action.in_(["next", "previous"])))
async def handle_my_ads(
        callback: types.CallbackQuery,
        callback_data: AdsCallbackData,
        state: FSMContext,
        admin: bool
):
    await clear_dialog(state=state)
    cached_ads = CachedAds()
    if callback_data.action == "next":
        data = cached_ads.get_next(index=callback_data.index, user_id=callback.from_user.id)
    else:
        data = cached_ads.get_previous(index=callback_data.index, user_id=callback.from_user.id)
    if data:
        text, type_, media = get_text_for_ads_message(data=data)
        await send_media_group_and_push_messages_to_state(state=state, media=media, callback=callback)
        reply_markup = get_my_ads_kb(
            id_=data.id,
            type_=type_,
            index=callback_data.index + 1
        )
    else:
        text="Нет объявлений в данной категории"
        reply_markup = get_main_kb(admin=admin)
    await push_message_to_state(
        await callback.message.answer(text=text, reply_markup=reply_markup),
        state=state
    )

#todo нужно ли передавать индекс
@router.callback_query(AdsCallbackData.filter(F.action == "change_ads"))
async def change_ads(callback: types.CallbackQuery, state: FSMContext, callback_data: AdsCallbackData):
    type_ = callback_data.type_
    id_ = callback_data.id
    await state.update_data(id_=id_, type_=type_)
    reply_markup = get_change_kb(id_=id_, type_=type_)
    await push_message_to_state(
        await callback.message.answer(text="Что хотите изменить?", reply_markup=reply_markup),
        state=state
    )


@router.callback_query(ChangeCallbackData.filter())
async def handle_change_ads(callback: types.CallbackQuery, state: FSMContext, callback_data: ChangeCallbackData):
    await clear_dialog(state=state)
    new_state, text = get_state_and_text(callback_data.action)
    await state.set_state(new_state)
    await push_message_to_state(
        await callback.message.answer(text=text),
        state=state
    )


@router.message(ChangeState.city)
async def handle_change_city(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    new_city = message.text
    data = await get_ads_by_id_and_type(state)
    data.city = new_city
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(f"Город изменен\nОжидайте подтверждения администратором", reply_markup=reply_markup),
        state=state
    )


@router.message(ChangeState.district)
async def handle_change_district(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    new_district = str(message.text)
    data = await get_ads_by_id_and_type(state)
    data.district = new_district
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(f"Район изменен\nОжидайте подтверждения администратором", reply_markup=reply_markup),
        state=state
    )


@router.message(ChangeState.info)
async def handle_change_info(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    new_info = str(message.text)
    data = await get_ads_by_id_and_type(state)
    data.info = new_info
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(f"Описание изменено\nОжидайте подтверждения администратором", reply_markup=reply_markup),
        state=state
    )


@router.message(ChangeState.address)
async def handle_change_address(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    new_address = str(message.text)
    data = await get_ads_by_id_and_type(state)
    data.address = new_address
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(f"Адрес изменен\nОжидайте подтверждения администратором", reply_markup=reply_markup),
        state=state
    )


@router.message(ChangeState.price)
async def handle_change_price(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    if not message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Стоимость должна быть целым числом."),
            state=state
        )
        await message.delete()
        return
    new_price = float(message.text)
    data = await get_ads_by_id_and_type(state)
    data.price = new_price
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(f"Цена изменена\nОжидайте подтверждения администратором", reply_markup=reply_markup),
        state=state
    )


@router.message(ChangeState.number_of_rooms)
async def handle_change_number_of_rooms(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    if not message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Количество комнат должно быть целым числом."),
            state=state
        )
        await message.delete()
        return
    new_rooms = int(message.text)
    data = await get_ads_by_id_and_type(state)
    data.rooms = new_rooms
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(text=f"Количество комнат изменено\nОжидайте подтверждения администратором",
                             reply_markup=reply_markup),
        state=state
    )


@router.message(ChangeState.the_general_area)
async def handle_change_the_general_area(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    the_general_area = float(message.text)
    data = await get_ads_by_id_and_type(state)
    data.the_general_area = the_general_area
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(text="Площадь изменена\nОжидайте подтверждения администратором",
                             reply_markup=reply_markup),
        state=state
    )



@router.message(ChangeState.floor)
async def handle_change_floor(message: types.Message, state: FSMContext, admin: bool):
    await clear_dialog(state=state)
    if not message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Отправьте число."),
            state=state
        )
        await message.delete()
        return
    floor = int(message.text)
    data = await get_ads_by_id_and_type(state)
    data.floor = floor
    data.verification = False
    await data.update()
    await message.delete()
    reply_markup = get_main_kb(admin)
    await push_message_to_state(
        await message.answer(text="Этаж изменен\nОжидайте подтверждения администратором",
                             reply_markup=reply_markup),
        state=state
    )
