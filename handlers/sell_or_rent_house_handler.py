from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from callbacks import TypeRealtyCallbackData
from core import User
from core.houses.models import House
from keyboards.clear_state_keyboard import get_clear_state_kb
from keyboards.main_keyboard import get_main_kb
from states import DoHouse
from utilits import clear_dialog, push_message_to_state, get_photos


router = Router()


@router.callback_query(TypeRealtyCallbackData.filter(F.action.in_(["sell_house", "pass_house"])))
async def sell_house(callback: types.CallbackQuery, state: FSMContext, callback_data: TypeRealtyCallbackData):
    await clear_dialog(state=state)
    reply_markup = get_clear_state_kb()
    if callback_data.action == "pass_house":
        await state.update_data(rent=True)
    else:
        await state.update_data(sale=True)
    await state.set_state(DoHouse.city)
    await push_message_to_state(
        await callback.message.answer(text="В каком городе находится дом?", reply_markup=reply_markup),
        state=state
    )



@router.message(DoHouse.city)
async def send_city_house(message: types.Message, state: FSMContext):
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
    await state.set_state(DoHouse.district)
    await push_message_to_state(
        await message.answer("В каком районе находится дом?", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.district)
async def send_district_house(message: types.Message, state: FSMContext):
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
    await state.set_state(DoHouse.number_of_rooms)
    await push_message_to_state(
        await message.answer("Количество комнат в доме?", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.number_of_rooms)
async def send_number_of_rooms_house(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    if not message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Количество комнат должно быть целым числом."),
            state=state
        )
        await message.delete()
        return
    await state.update_data(number_of_rooms=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoHouse.the_general_area)
    await push_message_to_state(
        await message.answer("Введите общую площадь дома", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.the_general_area)
async def send_the_general_area_house(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    if not message.text.isdigit():
        await push_message_to_state(
            await message.answer(text="Ошибка! Общая площадь должна быть числом."),
            state=state
        )
        await message.delete()
        return
    await state.update_data(the_general_area=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoHouse.price)
    data = await state.get_data()
    text = "Введите стоимость аренды дома" if data.get("rent") else "Введите стоимость продажи дома"
    await push_message_to_state(
        await message.answer(text, reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.price)
async def send_price_house(message: types.Message, state: FSMContext):
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
    await state.set_state(DoHouse.info)
    await push_message_to_state(
        await message.answer("Отправьте дополнительную информацию", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.info)
async def send_info_house(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    await state.update_data(info=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoHouse.address)
    await push_message_to_state(
        await message.answer("Уточните адрес дома", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.address)
async def send_address_house(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    await state.update_data(address=message.text)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoHouse.photo1)
    await push_message_to_state(
        await message.answer("Отправьте фото №1", reply_markup=reply_markup),
        state=state
    )
    await message.delete()



@router.message(DoHouse.photo1, F.content_type == ContentType.PHOTO)
async def send_photo_one_house(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    file_id = message.photo[-1].file_id
    photo = await message.bot.get_file(file_id)
    flat_photo = photo.file_id
    fpath = f"photos/{flat_photo}.jpg"
    await message.bot.download(file=message.photo[-1], destination=fpath)
    await state.update_data(photo1=flat_photo)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoHouse.photo2)
    await push_message_to_state(
        await message.answer("Отправьте фото №2", reply_markup=reply_markup),
        state=state
    )
    await message.delete()


@router.message(DoHouse.photo2, F.content_type == ContentType.PHOTO)
async def send_photo_two_house(message: types.Message, state: FSMContext):
    await clear_dialog(state=state)
    file_id = message.photo[-1].file_id
    photo = await message.bot.get_file(file_id)
    flat_photo = photo.file_id
    fpath = f"photos/{flat_photo}.jpg"
    await message.bot.download(file=message.photo[-1], destination=fpath)
    await state.update_data(photo2=flat_photo)
    reply_markup = get_clear_state_kb()
    await state.set_state(DoHouse.photo3)
    await push_message_to_state(
        await message.answer("Отправьте фото №3", reply_markup=reply_markup),
        state=state
    )
    await message.delete()



@router.message(DoHouse.photo3, F.content_type == ContentType.PHOTO)
async def send_photo_three_house(message: types.Message, state: FSMContext, admin: bool, user: User):
    await clear_dialog(state=state)
    file_id = message.photo[-1].file_id
    photo = await message.bot.get_file(file_id)
    flat_photo = photo.file_id
    fpath = f"photos/{flat_photo}.jpg"
    await message.bot.download(file=message.photo[-1], destination=fpath)
    await state.update_data(photo3=flat_photo)
    await state.set_state(DoHouse.photo3)
    data = await state.get_data()
    house = House(
        user_id=message.from_user.id,
        user_name=message.from_user.username,
        city=str(data.get("city")),
        district=str(data.get("district")),
        rooms=int(data.get("number_of_rooms")),
        the_general_area=float(data.get("the_general_area")),
        price=int(data.get("price")),
        info=str(data.get("info")),
        sale=data.get("sale", False),
        rent=data.get("rent", False),
        photos=await get_photos(state=state),
        address=data.get("address"),
        phone=user.phone
    )
    await house.add()
    await state.clear()
    reply_markup = get_main_kb(admin=admin)
    text="Объявление добавлено и отправлено на проверку. После одобрения, ваше объявление попадет в общую ленту"
    await push_message_to_state(
        await message.answer(text=text, reply_markup=reply_markup),
        state=state
    )
    await message.delete()