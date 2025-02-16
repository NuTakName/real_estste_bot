from aiogram.fsm.state import StatesGroup, State


class DoFlat(StatesGroup):
    city = State()
    district = State()
    number_of_rooms = State()
    the_general_area = State()
    floor = State()
    price = State()
    info = State()
    address = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()



class DoHouse(StatesGroup):
    city = State()
    district = State()
    number_of_rooms = State()
    the_general_area = State()
    price = State()
    info = State()
    address = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()


class DoGarage(StatesGroup):
    city = State()
    district = State()
    price = State()
    info = State()
    address = State()
    photo1 = State()
    photo2 = State()
    photo3 = State()


class RejectAds(StatesGroup):
    reason = State()


class ChangeState(StatesGroup):
    city = State()
    district = State()
    price = State()
    info = State()
    address = State()
    number_of_rooms = State()
    the_general_area = State()
    floor = State()
