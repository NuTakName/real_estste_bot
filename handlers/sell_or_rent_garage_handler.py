from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from callbacks import TypeRealtyCallbackData
from core import User
from core.garage.models import Garage
from keyboards.clear_state_keyboard import get_clear_state_kb
from keyboards.main_keyboard import get_main_kb
from states import DoGarage
from utilits import clear_dialog, push_message_to_state, get_photos

router = Router()


@router.callback_query(TypeRealtyCallbackData.filter(F.action.in_(["sell_garage", "pass_garage"])))
async def sell_garage(callback: types.CallbackQuery, state: FSMContext, callback_data: TypeRealtyCallbackData):
    await clear_dialog(state=state)
    reply_markup = get_clear_state_kb()
    if callback_data.action == "pass_garage":
        await state.update_data(rent=True)
    else:
        await state.update_data(sale=True)
    await state.set_state(DoGarage.city)
    await push_message_to_state(
        await callback.message.answer(text="В каком городе находится гараж?", reply_markup=reply_markup),
        state=state
    )


@router.message(DoGarage.city)
async def send_city_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    if message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Введите название города, а не число."),
            state=state
        )
        await message.delete()
        return
    await state.update_data(city=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.district)
    await push_message_to_state(
        await message.answer("В каком районе находится гараж?", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoGarage.district)
async def send_district_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    if message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Введите название района, а не число."),
            state=state
        )
        await message.delete()
        return
    await state.update_data(district=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.price)
    data = await state.get_data()
    text = "Введите стоимость аренды гаража" if data.get("rent") else "Введите стоимость продажи гаража"
    await push_message_to_state(
        await message.answer(text=text, reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoGarage.price)
async def send_price_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    if not message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Стоимость должна быть целым числом."),
            state=state
        )
        await message.delete()
        return
    await state.update_data(price=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.info)
    await push_message_to_state(
        await message.answer("Отправьте дополнительную информацию", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoGarage.info)
async def send_info_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    await state.update_data(info=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.address)
    await push_message_to_state(
        await message.answer("Уточните адрес гаража", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoGarage.address)
async def send_address_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    await state.update_data(address=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.photo1)
    await push_message_to_state(
        await message.answer("Отправьте фото №1", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoGarage.photo1, F.content_type == ContentType.PHOTO)
async def send_photo_one_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    file_id = message.photo[-1].file_id
    photo = await message.bot.get_file(file_id)
    flat_photo = photo.file_id
    fpath = f"photos/{flat_photo}.jpg"
    await message.bot.download(file=message.photo[-1], destination=fpath)
    await state.update_data(photo1=flat_photo)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.photo2)
    await push_message_to_state(
        await message.answer("Отправьте фото №2", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoGarage.photo2, F.content_type == ContentType.PHOTO)
async def send_photo_two_garage(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    file_id = message.photo[-1].file_id
    photo = await message.bot.get_file(file_id)
    flat_photo = photo.file_id
    fpath = f"photos/{flat_photo}.jpg"
    await message.bot.download(file=message.photo[-1], destination=fpath)
    await state.update_data(photo2=flat_photo)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoGarage.photo3)
    await push_message_to_state(
        await message.answer("Отправьте фото №3", reply_markup=reply_markup),
        state=state
    )
    await message.delete()



@router.message(DoGarage.photo3, F.content_type == ContentType.PHOTO)
async def send_photo_three_garage(message: types.Message, state: FSMContext, admin: bool, user: User):
    await clear_dialog(state=state)
    file_id = message.photo[-1].file_id
    photo = await message.bot.get_file(file_id)
    flat_photo = photo.file_id
    fpath = f"photos/{flat_photo}.jpg"
    await message.bot.download(file=message.photo[-1], destination=fpath)
    await state.update_data(photo3=flat_photo)
    await state.set_state(DoGarage.photo3)
    data = await state.get_data()
    flat = Garage(
        user_id=message.from_user.id,
        user_name=message.from_user.username,
        city=str(data.get("city")),
        district=str(data.get("district")),
        price=int(data.get("price")),
        info=str(data.get("info")),
        sale=data.get("sale", False),
        rent=data.get("rent", False),
        photos=await get_photos(state=state),
        address=data.get("address"),
        phone=user.phone
    )
    await flat.add()
    await state.clear()
    reply_markup = get_main_kb(admin=admin)
    text = "Объявление добавлено и отправлено на проверку. После ободрения, ваше объявление попадет в общую ленту"
    await push_message_to_state(
        await message.answer(text=text, reply_markup=reply_markup),
        state=state
    )
    await message.delete()