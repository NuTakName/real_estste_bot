from cached_data.sigleton import Singleton
from core.houses.models import House

class CachedHouse(metaclass=Singleton):
    cached_sale_house: dict = {}
    cached_rent_house: dict = {}

    async def loads_data_houses(self):
        sale_houses, rent_houses = await House.get_houses()
        self.cached_sale_house = sale_houses
        self.cached_rent_house = rent_houses

    async def get(self, action: str) -> House:
        if self.cached_sale_house is None or self.cached_rent_house is None:
            await self.loads_data_houses()
        houses = self.cached_sale_house if action == "buy_house" else self.cached_rent_house
        return next(iter(houses.values()), None) if houses else None


    def get_next(self, action: str, index: int) -> House | None:
        house = self.cached_sale_house if action == "buy_house" else self.cached_rent_house
        house_ids = list(house.keys())
        next_index = (index + 1) % len(house_ids)
        return house[house_ids[next_index]]

    def get_previous(self, action: str, index: int) -> House | None:
        house = self.cached_sale_house if action == "buy_house" else self.cached_rent_house
        house_ids = list(house.keys())
        previous_index = (index - 1) % len(house_ids)
        return house[house_ids[previous_index]]