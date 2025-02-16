from typing import Union

from cached_data.sigleton import Singleton
from core.garage.models import *
from core.houses.models import *
from core.flats.models import *


class CachedAds(metaclass=Singleton):
    data: dict = {}

    async def loads_data(self):
        data = await Garage.get_ads()
        self.data = data


    async def get(self, user_id: int | None = None):
        if self.data is None:
            await self.loads_data()
        values = self.data.get(user_id)
        return next(iter(values), None) if values else None


    def get_next(self, index: int, user_id: int) -> Union[Garage, House, Flat] | None:
        ads_ids = self.data.get(user_id)
        next_index = (index + 1) % len(ads_ids)
        return ads_ids[next_index]


    def get_previous(self, index: int, user_id: int) -> Union[Garage, House, Flat] | None:
        ads_ids = self.data.get(user_id)
        previous_index = (index - 1) % len(ads_ids)
        return ads_ids[previous_index]

    def remove_ads(self, user_id: int):
        self.data[user_id].pop(0)

    def get_by_index(self, index: int, user_id: int) -> Union[Garage, House, Flat] | None:
        ads_ids = self.data.get(user_id)
        if ads_ids and 0 <= index < len(ads_ids):
            return ads_ids[index]
        return None
